"use strict";

var Bacon = require('baconjs'),
    $ = require('jquery'),
    R = require('ramda'),
    _ = require('lodash');

// Bacon.js is an npm module, but only extends jQuery if it's a global object
// So we need to add extend jQuery with Bacon methods manually
$.extend($.fn, Bacon.$);

function keyCodeIs (keyCodes) {
    return function(event) {
        for (var i = 0; i < keyCodes.length; i++) {
            if (event.which === keyCodes[i]) {
                return true;
            }
        }
        return false;
    };
}
exports.keyCodeIs = keyCodeIs;

var isEnterKey = exports.isEnterKey = keyCodeIs([13]);
exports.isEscKey = keyCodeIs([27]);

exports.not = function(staticValue, streamValue) {
    return staticValue !== streamValue;
};

var isDefined = exports.isDefined = R.not(_.isUndefined);

var isDefinedNonEmpty = exports.isDefinedNonEmpty = R.and(R.not(_.isUndefined), R.not(R.eq('')));

var isUndefined = exports.isUndefined = _.isUndefined;

var isUndefinedOrEmpty = exports.isUndefinedOrEmpty = R.or(_.isUndefined, R.eq(''));

// Used to get object property values
// Needed for keys with '.' in them, as Bacon will treat a '.' a in key as an
// indication that there are nested objects
var getValueForKey = exports.getValueForKey = function(key) {
    return function (object) { return object[key]; };
};

exports.isPropertyUndefined = function(key) {
    return R.or(isUndefined, R.compose(isUndefined, getValueForKey(key)));
};

exports.fetchFromIdStream = function (idStream, fetchFn, undefinedMapping, errorMapping) {
    return Bacon.mergeAll(
        idStream
            .filter(isDefined)
            .flatMap(fetchFn)
            .mapError(errorMapping),
        idStream
            .filter(isUndefined)
            .map(undefinedMapping));
};

exports.ajaxRequest = function(options) {
    return function(payload) {
        var req = $.ajax(_.defaults({}, options, {
            data: payload
        }));
        return Bacon.fromPromise(req);
    };
};

exports.jsonRequest = function(verb, url) {
    return function(payload) {
        // url wasn't specififed
        if (arguments.length == 2) {
            payload = url;
        }

        if (verb != 'GET') {
            payload = JSON.stringify(payload);
        }

        var req = $.ajax({
            method: verb,
            url: url,
            contentType: 'application/json',
            data: payload
        });

        return Bacon.fromPromise(req);
    };
};

// The ``jsonRequest`` function is used for making
// requests to a static URL with a body or query
// arguments generated by stream processing.
// ``getJsonFromUrl``, on the other hand, is used
// for making simple GET requests where the URL
// is generated by stream processing.
exports.getJsonFromUrl = function(url) {
    var req = $.ajax({
            url: url,
            contentType: 'application/json'
        });
    return Bacon.fromPromise(req);
};

// binds a number of form controls together with
// a button to provide a consistent form submission
// experience
exports.enterOrClickEventStream = function(options) {
    var inputs = $(options.inputs),
        button = $(options.button),
        enterKeyPressStream = inputs
            .asEventStream("keyup")
            .filter(isEnterKey),

        performSearchClickStream = button.asEventStream("click"),

        triggerEventStream = enterKeyPressStream.merge(
            performSearchClickStream);

    // When enter is pressed blur the text input that caused it to close
    // any touch keyboards that may be open
    enterKeyPressStream.map('.target').map($).onValue('.blur');

    return triggerEventStream;
};

exports.leafletEventStream = function(leafletThing, event) {
    return Bacon.fromBinder(function (handler) {
        leafletThing.on(event, handler);
        return function() {
            return leafletThing.off(event, handler);
        };
    });
};

exports.leafletSingleClickStream = function(leafletThing, doubleClickTime) {
    // Return clicks on 'leafletThing' that aren't double clicks.
    // We can't know what time interval the OS uses for double clicks,
    // so we do our own interval checking.
    var clickStream = exports.leafletEventStream(leafletThing, 'click'),
        singleClickStream = clickStream.bufferWithTimeOrCount(doubleClickTime, 2)
            .filter(function (clicks) {
                return clicks.length < 2;
            })
            .map(_.first);
    return singleClickStream;
};

exports.triggeredObjectStream = function (obj) {
    var subscribers = [],
        stream = new Bacon.EventStream(function (subscriber) {
            subscribers.push(subscriber);
            return function() {
                subscribers = _.without(subscribers, subscriber);
            };
        });

    stream.trigger = function () {
        _.each(subscribers, function (subscriber) {
            subscriber(new Bacon.Next(obj));
        });
    };

    return stream;
};
