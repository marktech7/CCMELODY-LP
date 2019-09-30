// This is a mock QWebChannel
var qt = {webChannelTransport: 1};
var QWebChannel = function (transport, callback) {
  callback({objects: {mediaWatcher: {}}});
};
