/**
 * display.js is the main Javascript file that is used to drive the display.
 */

/**
 * Background type enumeration
 */
var BackgroundType = {
  Transparent: "transparent",
  Solid: "solid",
  Gradient: "gradient",
  Video: "video",
  Image: "image"
};

/**
 * Gradient type enumeration
 */
var GradientType = {
  Horizontal: "horizontal",
  LeftTop: "leftTop",
  LeftBottom: "leftBottom",
  Vertical: "vertical",
  Circular: "circular"
};

/**
 * Horizontal alignment enumeration
 */
var HorizontalAlign = {
  Left: 0,
  Right: 1,
  Center: 2,
  Justify: 3
};

/**
 * Vertical alignment enumeration
 */
var VerticalAlign = {
  Top: 0,
  Middle: 1,
  Bottom: 2
};

/**
 * Transition type enumeration
 */
var TransitionType = {
  Fade: 0,
  Slide: 1,
  Convex: 2,
  Concave: 3,
  Zoom: 4
};

/**
 * Transition speed enumeration
 */
var TransitionSpeed = {
  Normal: 0,
  Fast: 1,
  Slow: 2
};


/**
 * Transition direction enumeration
 */
var TransitionDirection = {
  Horizontal: 0,
  Vertical: 1
};

/**
 * Audio state enumeration
 */
var AudioState = {
  Playing: "playing",
  Paused: "paused",
  Stopped: "stopped"
};

/**
 * Transition state enumeration
 */
var TransitionState = {
  EntranceTransition: "entranceTransition",
  NoTransition: "noTransition",
  ExitTransition: "exitTransition"
};

/**
 * Animation state enumeration
 */
var AnimationState = {
  NoAnimation: "noAnimation",
  ScrollingText: "scrollingText",
  NonScrollingText: "noScrollingText"
};

/**
 * Alert location enumeration
 */
var AlertLocation = {
  Top: 0,
  Middle: 1,
  Bottom: 2
};

/**
 * Alert state enumeration
 */
var AlertState = {
  Displaying: "displaying",
  NotDisplaying: "notDisplaying"
};

/**
 * Alert delay enumeration
 */
var AlertDelay = {
  FiftyMilliseconds: 50,
  OneSecond: 1000,
  OnePointFiveSeconds: 1500
};

/**
 * Return an array of elements based on the selector query
 * @param {string} selector - The selector to find elements
 * @returns {array} An array of matching elements
 */
function $(selector) {
  return Array.from(document.querySelectorAll(selector));
}

/**
 * Build linear gradient CSS
 * @private
 * @param {string} startDir - Starting direction
 * @param {string} endDir - Ending direction
 * @param {string} startColor - The starting color
 * @param {string} endColor - The ending color
 * @returns {string} A string of the gradient CSS
 */
function _buildLinearGradient(startDir, endDir, startColor, endColor) {
  return "-webkit-gradient(linear, " + startDir + ", " + endDir + ", from(" + startColor + "), to(" + endColor + ")) fixed";
}

/**
 * Build radial gradient CSS
 * @private
 * @param {string} width - Width of the gradient
 * @param {string} startColor - The starting color
 * @param {string} endColor - The ending color
 * @returns {string} A string of the gradient CSS
 */
function _buildRadialGradient(width, startColor, endColor) {
  return "-webkit-gradient(radial, " + width + " 50%, 100, " + width + " 50%, " + width + ", from(" + startColor + "), to(" + endColor + ")) fixed";
}

/**
 * Get a style value from an element (computed or manual)
 * @private
 * @param {Object} element - The element whose style we want
 * @param {string} style - The name of the style we want
 * @returns {(Number|string)} The style value (type depends on the style)
 */
function _getStyle(element, style) {
  return document.defaultView.getComputedStyle(element).getPropertyValue(style);
}

/**
 * Convert newlines to <br> tags
 * @private
 * @param {string} text - The text to parse
 * @returns {string} The text now with <br> tags
 */
function _nl2br(text) {
  return text.replace("\r\n", "\n").replace("\n", "<br>");
}

/**
 * Prepare text by creating paragraphs and calling _nl2br to convert newlines to <br> tags
 * @private
 * @param {string} text - The text to parse
 * @returns {string} The text now with <p> and <br> tags
 */
function _prepareText(text) {
  return "<p>" + _nl2br(text) + "</p>";
}

/**
 * Change a camelCaseString to a camel-case-string
 * @private
 * @param {string} text
 * @returns {string} the Un-camel-case-ified string
 */
function _fromCamelCase(text) {
  return text.replace(/([A-Z])/g, function (match, submatch) {
    return '-' + submatch.toLowerCase();
  });
}

/**
 * Create a CSS style
 * @private
 * @param {string} selector - The selector for this style
 * @param {Object} rules - The rules to apply to the style
 */
function _createStyle(selector, rules) {
  var style;
  var id = selector.replace("#", "").replace(" .", "-").replace(".", "-").replace(" ", "_");
  if ($("style#" + id).length != 0) {
    style = $("style#" + id)[0];
  }
  else {
    style = document.createElement("style");
    document.getElementsByTagName("head")[0].appendChild(style);
    style.type = "text/css";
    style.id = id;
  }
  var rulesString = selector + " { ";
  for (var key in rules) {
    var ruleValue = rules[key];
    var ruleKey = _fromCamelCase(key);
    rulesString += "" + ruleKey + ": " + ruleValue + ";";
  }
  rulesString += " } ";
  if (style.styleSheet) {
    style.styleSheet.cssText = rulesString;
  }
  else {
    style.appendChild(document.createTextNode(rulesString));
  }
}

/**
 * An audio player with a play list
 */
var AudioPlayer = function (audioElement) {
  this._audioElement = null;
  this._eventListeners = {};
  this._playlist = [];
  this._currentTrack = null;
  this._canRepeat = false;
  this._state = AudioState.Stopped;
  this.createAudioElement();
};

/**
 * Call all listeners associated with this event
 * @private
 * @param {object} event - The event that was emitted
 */
AudioPlayer.prototype._callListener = function (event) {
  if (this._eventListeners.hasOwnProperty(event.type)) {
    this._eventListeners[event.type].forEach(function (listener) {
      listener(event);
    });
  }
  else {
    console.warn("Received unknown event \"" + event.type + "\", doing nothing.");
  }
};

/**
 * Create the <audio> element that is used to play the audio
 */
AudioPlayer.prototype.createAudioElement = function () {
  this._audioElement = document.createElement("audio");
  this._audioElement.addEventListener("ended", this.onEnded);
  this._audioElement.addEventListener("ended", this._callListener);
  this._audioElement.addEventListener("timeupdate", this._callListener);
  this._audioElement.addEventListener("volumechange", this._callListener);
  this._audioElement.addEventListener("durationchange", this._callListener);
  this._audioElement.addEventListener("loadeddata", this._callListener);
  document.addEventListener("complete", function(event) {
    document.body.appendChild(this._audioElement);
  });
};
AudioPlayer.prototype.addEventListener = function (eventType, listener) {
  this._eventListeners[eventType] = this._eventListeners[eventType] || [];
  this._eventListeners[eventType].push(listener);
};
AudioPlayer.prototype.onEnded = function (event) {
  this.nextTrack();
};
AudioPlayer.prototype.setCanRepeat = function (canRepeat) {
  this._canRepeat = canRepeat;
};
AudioPlayer.prototype.clearTracks = function () {
  this._playlist = [];
};
AudioPlayer.prototype.addTrack = function (track) {
  this._playlist.push(track);
};
AudioPlayer.prototype.nextTrack = function () {
  if (!!this._currentTrack) {
    var trackIndex = this._playlist.indexOf(this._currentTrack);
    if ((trackIndex + 1 >= this._playlist.length) && this._canRepeat) {
      this.play(this._playlist[0]);
    }
    else if (trackIndex + 1 < this._playlist.length) {
      this.play(this._playlist[trackIndex + 1]);
    }
    else {
      this.stop();
    }
  }
  else if (this._playlist.length > 0) {
    this.play(this._playlist[0]);
  }
  else {
    console.warn("No tracks in playlist, doing nothing.");
  }
};
AudioPlayer.prototype.play = function () {
  if (arguments.length > 0) {
    this._currentTrack = arguments[0];
    this._audioElement.src = this._currentTrack;
    this._audioElement.play();
    this._state = AudioState.Playing;
  }
  else if (this._state == AudioState.Paused) {
    this._audioElement.play();
    this._state = AudioState.Playing;
  }
  else {
    console.warn("No track currently paused and no track specified, doing nothing.");
  }
};

/**
 * Pause
 */
AudioPlayer.prototype.pause = function () {
  this._audioElement.pause();
  this._state = AudioState.Paused;
};

/**
 * Stop playing
 */
AudioPlayer.prototype.stop = function () {
  this._audioElement.pause();
  this._audioElement.src = "";
  this._state = AudioState.Stopped;
};

/**
 * The Display object is what we use from OpenLP
 */
var Display = {
  _slidesContainer: null,
  _footerContainer: null,
  _backgroundsContainer: null,
  _alerts: [],
  _slides: {},
  _alertSettings: {},
  _alertState: AlertState.NotDisplaying,
  _transitionState: TransitionState.NoTransition,
  _animationState: AnimationState.NoAnimation,
  _doTransitions: false,
  _doItemTransitions: false,
  _themeApplied: true,
  _revealConfig: {
    margin: 0.0,
    minScale: 1.0,
    maxScale: 1.0,
    controls: false,
    progress: false,
    history: false,
    keyboard: false,
    overview: false,
    center: false,
    touch: false,
    help: false,
    transition: "none",
    backgroundTransition: "none",
    viewDistance: 9999,
    width: "100%",
    height: "100%"
  },
  /**
   * Start up reveal and do any other initialisation
   */
  init: function (doTransitions=false, doItemtransitions=false) {
    var globalBackground = $("#global-background")[0];
    globalBackground.style.cssText = "";
    globalBackground.style.setProperty("background", "black");
    Display._slidesContainer = $(".slides")[0];
    Display._footerContainer = $(".footer")[0];
    Display._backgroundsContainer = $(".backgrounds")[0];
    Display._doTransitions = doTransitions;
    Reveal.initialize(Display._revealConfig);
    Display.setItemTransition(doItemtransitions && doTransitions);
    displayWatcher.setInitialised(true);
  },
  /**
   * Reinitialise Reveal
   */
  reinit: function () {
    Reveal.sync();
    // Python expects to be on first page after reinit
    Reveal.slide(0);
  },
  /**
   * Enable/Disable item transitions
   */
  setItemTransition: function (enable) {
    Display._doItemTransitions = enable;
    var body = $("body")[0];
    if (enable) {
      body.classList.add("transition");
      Reveal.configure({"backgroundTransition": "fade", "transitionSpeed": "default"});
    } else {
      body.classList.remove("transition");
      Reveal.configure({"backgroundTransition": "none"});
    }
  },
  /**
   * Clear the current list of slides
  */
  clearSlides: function () {
    Display._slidesContainer.innerHTML = "";
    Display._clearSlidesList();
  },
  /**
   * Clear the current list of slides
  */
  _clearSlidesList: function () {
    Display._footerContainer.innerHTML = "";
    Display._slides = {};
  },
  /**
   * Add new item/slides, replacing the old one
   * Clears current list of slides but allows time for a transition animation
   * Items are ordered newest to oldest in the slides container
   * @param {element} new_slides - New slides to display
   * @param {element} is_text - Used to decide if the theme main area constraints should apply
  */
  replaceSlides: function (new_slides, is_text=false) {
    if (Display._doItemTransitions) {
      new_slides.setAttribute('data-transition', "fade");
      new_slides.setAttribute('data-transition-speed', "default");
    }
    new_slides.classList.add("future");
    Display.applyTheme(new_slides, is_text);
    Display._slidesContainer.prepend(new_slides);
    var currentSlide = Reveal.getIndices();
    if (Display._doItemTransitions && Display._slidesContainer.children.length >= 2) {
      // Set the slide one section ahead so we'll stay on the old slide after reinit
      Reveal.slide(1, currentSlide.v);
      Display.reinit();
      // Timeout to allow time to transition before deleting the old slides
      setTimeout (Display._removeLastSection, 5000);
    } else {
      Reveal.slide(0, currentSlide.v);
      Reveal.sync();
      Display._removeLastSection();
    }
  },
  /**
   * Removes the last slides item if there are more than one
  */
  _removeLastSection: function () {
    if (Display._slidesContainer.children.length > 1) {
      Display._slidesContainer.lastChild.remove();
    }
  },
  /**
   * Checks if the present slide content fits within the slide
  */
  doesContentFit: function () {
    var currSlide = $("section.text-slides");
    if (currSlide.length === 0) {
      currSlide = Display._footerContainer;
    } else {
      currSlide = currSlide[0];
    }
    return currSlide.clientHeight >= currSlide.scrollHeight;
  },
  /**
   * Generate the OpenLP startup splashscreen
   * @param {string} bg_color - The background color
   * @param {string} image - Path to the splash image
   */
  setStartupSplashScreen: function(bg_color, image) {
    Display._clearSlidesList();
    var section = document.createElement("section");
    section.setAttribute("id", 0);
    section.setAttribute("data-background", bg_color);
    section.setAttribute("style", "height: 100%; width: 100%;");
    var img = document.createElement('img');
    img.src = image;
    img.setAttribute("style", "position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; max-height: 100%; max-width: 100%");
    section.appendChild(img);
    Display._slides['0'] = 0;
    Display.replaceSlides(section);
  },
  /**
   * Set fullscreen image from path
   * @param {string} bg_color - The background color
   * @param {string} image - Path to the image
   */
  setFullscreenImage: function(bg_color, image) {
    Display.clearSlides();
    var section = document.createElement("section");
    section.setAttribute("id", 0);
    section.setAttribute("data-background", bg_color);
    section.setAttribute("style", "height: 100%; width: 100%;");
    var img = document.createElement('img');
    img.src = image;
    img.setAttribute("style", "height: 100%; width: 100%");
    section.appendChild(img);
    Display._slides['0'] = 0;
    Display.replaceSlides(parentSection);
  },
  /**
   * Set fullscreen image from base64 data
   * @param {string} bg_color - The background color
   * @param {string} image_data - base64 encoded image data
   */
  setFullscreenImageFromData: function(bg_color, image_data) {
    Display.clearSlides();
    var section = document.createElement("section");
    section.setAttribute("id", 0);
    section.setAttribute("data-background", bg_color);
    section.setAttribute("style", "height: 100%; width: 100%;");
    var img = document.createElement('img');
    img.src = 'data:image/png;base64,' + image_data;
    img.setAttribute("style", "height: 100%; width: 100%");
    section.appendChild(img);
    Display._slidesContainer.appendChild(section);
    Display._slides['0'] = 0;
    Display.reinit();
  },
  /**
   * Display an alert. If there's an alert already showing, add this one to the queue
   * @param {string} text - The alert text
   * @param {Object} JSON object - The settings for the alert object
  */
  alert: function (text, settings) {
    if (text == "") {
      return null;
    }
    if (Display._alertState === AlertState.Displaying) {
      console.debug("Adding to queue");
      Display.addAlertToQueue(text, settings);
    }
    else {
      console.debug("Displaying immediately");
      Display.showAlert(text, settings);
    }
  },
  /**
   * Show the alert on the screen
   * @param {string} text - The alert text
   * @param {Object} JSON object - The settings for the alert
  */
  showAlert: function (text, settings) {
    var alertBackground = $('#alert-background')[0];
    var alertText = $('#alert-text')[0];
    // create styles for the alerts from the settings
    _createStyle("#alert-background.settings", {
      backgroundColor: settings.backgroundColor,
      fontFamily: "'" + settings.fontFace + "'",
      fontSize: settings.fontSize.toString() + "pt",
      color: settings.fontColor
    });
    alertBackground.classList.add("settings");
    alertBackground.classList.replace("hide", "show");
    alertText.innerHTML = text;
    Display.setAlertLocation(settings.location);
    Display._transitionState = TransitionState.EntranceTransition;
    /* Check if the alert is a queued alert */
    if (Display._alertState !== AlertState.Displaying) {
      Display._alertState = AlertState.Displaying;
    }
    alertBackground.addEventListener('transitionend', Display.alertTransitionEndEvent, false);
    alertText.addEventListener('animationend', Display.alertAnimationEndEvent, false);
    /* Either scroll the alert, or make it disappear at the end of its time */
    if (settings.scroll) {
      Display._animationState = AnimationState.ScrollingText;
      var animationSettings = "alert-scrolling-text " + settings.timeout +
                              "s linear 0.6s " + settings.repeat + " normal";
      alertText.style.animation = animationSettings;
    }
    else {
      Display._animationState = AnimationState.NonScrollingText;
      alertText.classList.replace("hide", "show");
      setTimeout (function () {
        Display._animationState = AnimationState.NoAnimation;
        Display.hideAlert();
      }, settings.timeout * AlertDelay.OneSecond);
    }
  },
  /**
   * Hide the alert at the end
   */
  hideAlert: function () {
    var alertBackground = $('#alert-background')[0];
    var alertText = $('#alert-text')[0];
    Display._transitionState = TransitionState.ExitTransition;
    alertText.classList.replace("show", "hide");
    alertBackground.classList.replace("show", "hide");
    alertText.style.animation = "";
    Display._alertState = AlertState.NotDisplaying;
  },
  /**
   * Add an alert to the alert queue
   * @param {string} text - The alert text to be displayed
   * @param {Object} setttings - JSON object containing the settings for the alert
   */
  addAlertToQueue: function (text, settings) {
    Display._alerts.push({text: text, settings: settings});
  },
  /**
   * The alertTransitionEndEvent called after a transition has ended
   */
  alertTransitionEndEvent: function (e) {
    e.stopPropagation();
    console.debug("Transition end event reached: " + Display._transitionState);
    if (Display._transitionState === TransitionState.EntranceTransition) {
      Display._transitionState = TransitionState.NoTransition;
    }
    else if (Display._transitionState === TransitionState.ExitTransition) {
      Display._transitionState = TransitionState.NoTransition;
      Display.hideAlert();
      Display.showNextAlert();
    }
  },
  /**
   * The alertAnimationEndEvent called after an animation has ended
   */
  alertAnimationEndEvent: function (e) {
    e.stopPropagation();
    Display.hideAlert();
  },
  /**
   * Set the location of the alert
   * @param {int} location - Integer number with the location of the alert on screen
   */
  setAlertLocation: function (location) {
    var alertContainer = $(".alert-container")[0];
    // Remove an existing location classes
    alertContainer.classList.remove("top");
    alertContainer.classList.remove("middle");
    alertContainer.classList.remove("bottom");
    // Apply the location class we want
    switch (location) {
      case AlertLocation.Top:
        alertContainer.classList.add("top");
        break;
      case AlertLocation.Middle:
        alertContainer.classList.add("middle");
        break;
      case AlertLocation.Bottom:
      default:
        alertContainer.classList.add("bottom");
        break;
    }
  },
  /**
  * Display the next alert in the queue
  */
  showNextAlert: function () {
    console.log("showNextAlert");
    if (Display._alerts.length > 0) {
      console.log("Showing next alert");
      var alertObject = Display._alerts.shift();
      Display._alertState = AlertState.DisplayingFromQueue;
      Display.showAlert(alertObject.text, alertObject.settings);
    }
    else {
      // For the tests
      return null;
    }
  },
  /**
   * Create a text slide.
   * @param {string} verse - The verse number, e.g. "v1"
   * @param {string} text - The HTML for the verse, e.g. "line1<br>line2"
   */
  _createTextSlide: function (verse, text) {
    var slide;
    var html = _prepareText(text);
    slide = document.createElement("section");
    slide.setAttribute("id", verse);
    slide.innerHTML = html;
    return slide;
  },
  /**
   * Set text slides.
   * @param {Object[]} slides - A list of slides to add as JS objects: {"verse": "v1", "text": "line 1\nline2"}
   */
  setTextSlides: function (slides) {
    Display._clearSlidesList();
    var slide_html;
    var parentSection = document.createElement("section");
    parentSection.classList = "text-slides";
    slides.forEach(function (slide) {
      slide_html = Display._createTextSlide(slide.verse, slide.text);
      parentSection.appendChild(slide_html);
      Display._slides[slide.verse] = parentSection.children.length - 1;
      if (slide.footer) {
        Display._footerContainer.innerHTML = slide.footer;
      }
    });
    Display.replaceSlides(parentSection, true);
  },
  /**
   * Set a single text slide. This changes the slide with no transition.
   * Prevents the need to reapply the theme if only changing content.
   * @param String slide - Text to put on the slide
   */
  setTextSlide: function (text) {
    if (Display._slides.hasOwnProperty("test-slide") && Object.keys(Display._slides).length === 1) {
      var slide = $("#" + "test-slide")[0];
      var html = _prepareText(text);
      if (slide.innerHTML != html) {
        slide.innerHTML = html;
      }
      if (!Display._themeApplied) {
        Display.applyTheme(slide.parent);
      }
    } else {
      Display._clearSlidesList();
      var slide_html;
      var parentSection = document.createElement("section");
      parentSection.classList = "text-slides";
      slide_html = Display._createTextSlide("test-slide", text);
      parentSection.appendChild(slide_html);
      Display._slides["test-slide"] = 0;
      Display.applyTheme(parentSection);
      Display._slidesContainer.innerHTML = "";
      Display._slidesContainer.prepend(parentSection);
      Display.reinit();
    }
  },
  /**
   * Set image slides
   * @param {Object[]} slides - A list of images to add as JS objects [{"path": "url/to/file"}]
   */
  setImageSlides: function (slides) {
    Display._clearSlidesList();
    var parentSection = document.createElement("section");
    slides.forEach(function (slide, index) {
      var section = document.createElement("section");
      section.setAttribute("id", index);
      section.setAttribute("data-background", "#000");
      section.setAttribute("style", "height: 100%; width: 100%;");
      var img = document.createElement('img');
      img.src = slide.path;
      img.setAttribute("style", "max-width: 100%; max-height: 100%; margin: 0; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);");
      section.appendChild(img);
      parentSection.appendChild(section);
      Display._slides[index.toString()] = index;
    });
    Display.replaceSlides(parentSection);
  },
  /**
   * Set a video
   * @param {Object} video - The video to show as a JS object: {"path": "url/to/file"}
   */
  setVideo: function (video) {
    Display._clearSlidesList();
    var section = document.createElement("section");
    section.setAttribute("data-background", "#000");
    var videoElement = document.createElement("video");
    videoElement.src = video.path;
    videoElement.preload = "auto";
    videoElement.setAttribute("id", "video");
    videoElement.setAttribute("style", "height: 100%; width: 100%;");
    videoElement.autoplay = false;
    // All the update methods below are Python functions, hence not camelCase
    videoElement.addEventListener("durationchange", function (event) {
      mediaWatcher.update_duration(event.target.duration);
    });
    videoElement.addEventListener("timeupdate", function (event) {
      mediaWatcher.update_progress(event.target.currentTime);
    });
    videoElement.addEventListener("volumeupdate", function (event) {
      mediaWatcher.update_volume(event.target.volume);
    });
    videoElement.addEventListener("ratechange", function (event) {
      mediaWatcher.update_playback_rate(event.target.playbackRate);
    });
    videoElement.addEventListener("ended", function (event) {
      mediaWatcher.has_ended(event.target.ended);
    });
    videoElement.addEventListener("muted", function (event) {
      mediaWatcher.has_muted(event.target.muted);
    });
    section.appendChild(videoElement);
    Display.replaceSlides(section);
  },
  /**
   * Play a video
   */
  playVideo: function () {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].play();
    }
  },
  /**
   * Pause a video
   */
  pauseVideo: function () {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].pause();
    }
  },
  /**
   * Stop a video
   */
  stopVideo: function () {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].pause();
      videoElem[0].currentTime = 0.0;
    }
  },
  /**
   * Go to a particular time in a video
   * @param seconds The position in seconds to seek to
   */
  seekVideo: function (seconds) {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].currentTime = seconds;
    }
  },
  /**
   * Set the playback rate of a video
   * @param rate A Double of the rate. 1.0 => 100% speed, 0.75 => 75% speed, 1.25 => 125% speed, etc.
   */
  setPlaybackRate: function (rate) {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].playbackRate = rate;
    }
  },
  /**
   * Set the volume
   * @param level The volume level from 0 to 100.
   */
  setVideoVolume: function (level) {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].volume = level / 100.0;
    }
  },
  /**
   * Mute the volume
   */
  toggleVideoMute: function () {
    var videoElem = $("#video");
    if (videoElem.length == 1) {
      videoElem[0].muted = !videoElem[0].muted;
    }
  },
  /**
   * Clear the background audio playlist
   */
  clearPlaylist: function () {
    var backgroundAudoElem = $("#background-audio");
    if (backgroundAudoElem.length == 1) {
      var audio = backgroundAudoElem[0];
      /* audio.playList */
    }
  },
  /**
   * Add background audio
   * @param files The list of files as objects in an array
   */
  addBackgroundAudio: function (files) {
  },
  /**
   * Go to a slide.
   * @param slide The slide number or name, e.g. "v1", 0
   */
  goToSlide: function (slide) {
    if (Display._slides.hasOwnProperty(slide)) {
      Reveal.slide(0, Display._slides[slide]);
    }
    else {
      Reveal.slide(0, slide);
    }
  },
  /**
   * Go to the next slide in the list
  */
  next: Reveal.nextFragment,
  /**
   * Go to the previous slide in the list
  */
  prev: Reveal.prevFragment,
  /**
   * Blank the screen
  */
  toBlack: function () {
    var documentBody = $("body")[0];
    documentBody.style.opacity = 1;
    if (!Reveal.isPaused()) {
      Reveal.togglePause();
    }
  },
  /**
   * Hide all but theme background
  */
  toTheme: function () {
    var documentBody = $("body")[0];
    documentBody.style.opacity = 1;
    Display._slidesContainer.style.opacity = 0;
    Display._footerContainer.style.opacity = 0;
    if (Reveal.isPaused()) {
      Reveal.togglePause();
    }
  },
  /**
   * Hide everything (CAUTION: Causes a invisible mouse barrier)
  */
  toTransparent: function () {
    Display._slidesContainer.style.opacity = 0;
    Display._footerContainer.style.opacity = 0;
    var documentBody = $("body")[0];
    documentBody.style.opacity = 0;
    if (!Reveal.isPaused()) {
      Reveal.togglePause();
    }
  },
  /**
   * Show the screen
  */
  show: function () {
    var documentBody = $("body")[0];
    documentBody.style.opacity = 1;
    Display._slidesContainer.style.opacity = 1;
    Display._footerContainer.style.opacity = 1;
    if (Reveal.isPaused()) {
      Reveal.togglePause();
    }
  },
  /**
   * Figure out how many lines can fit on a slide given the font size
   * @param fontSize The font size in pts
   */
  calculateLineCount: function (fontSize) {
    var p = $(".slides > section > section > p");
    if (p.length == 0) {
      Display.addSlide("v1", "Arky arky");
      p = $(".slides > section > section > p");
    }
    p = p[0];
    p.style.fontSize = "" + fontSize + "pt";
    var d = $(".slides > section")[0];
    var lh = parseFloat(_getStyle(p, "line-height"));
    var dh = parseFloat(_getStyle(d, "height"));
    return Math.floor(dh / lh);
  },
  /**
   * Prepare the theme for the next item to be added
   * @param theme The theme to be used
   */
  setTheme: function (theme) {
    if (Display._theme != theme) {
      Display._themeApplied = false;
      Display._theme = theme;
    }
  },
  /**
   * Apply the theme to the provided element
   * @param targetElement The target element to apply the theme (expected to be a <section> in the slides container)
   * @param is_text Used to decide if the main area constraints should be applied
   */
  applyTheme: function (targetElement, is_text=true) {
    Display._themeApplied = true;
    if (!Display._theme) {
      return;
    }
    // Set slide transitions
    var new_transition_type = "none",
        new_transition_speed = "default";
    if (!!Display._theme.display_slide_transition && Display._doTransitions) {
      switch (Display._theme.display_slide_transition_type) {
        case TransitionType.Fade:
          new_transition_type = "fade";
          break;
        case TransitionType.Slide:
          new_transition_type = "slide";
          break;
        case TransitionType.Convex:
          new_transition_type = "convex";
          break;
        case TransitionType.Concave:
          new_transition_type = "concave";
          break;
        case TransitionType.Zoom:
          new_transition_type = "zoom";
          break;
        default:
          new_transition_type = "fade";
      }
      switch (Display._theme.display_slide_transition_speed) {
        case TransitionSpeed.Normal:
          new_transition_speed = "default";
          break;
        case TransitionSpeed.Fast:
          new_transition_speed = "fast";
          break;
        case TransitionSpeed.Slow:
          new_transition_speed = "slow";
          break;
        default:
          new_transition_speed = "default";
      }
      switch (Display._theme.display_slide_transition_direction) {
        case TransitionDirection.Vertical:
          new_transition_type += "-vertical";
          break;
        case TransitionDirection.Horizontal:
        default:
          new_transition_type += "-horizontal";
      }
      if (Display._theme.display_slide_transition_reverse) {
        new_transition_type += "-reverse";
      }
    }
    var slides = targetElement.children;
    for (var i = 0; i < slides.length; i++) {
      slides[i].setAttribute("data-transition", new_transition_type);
      slides[i].setAttribute("data-transition-speed", new_transition_speed);
    }
    // Set the background
    var backgroundContent = "";
    var backgroundHtml = "";
    var globalBackground = $("#global-background")[0];
    globalBackground.style.setProperty("background", "black");
    switch (Display._theme.background_type) {
      case BackgroundType.Transparent:
        backgroundContent = "transparent";
        globalBackground.style.setProperty("background", "transparent");
        break;
      case BackgroundType.Solid:
        backgroundContent = Display._theme.background_color;
        break;
      case BackgroundType.Gradient:
        switch (Display._theme.background_direction) {
          case GradientType.Horizontal:
            backgroundContent = _buildLinearGradient("left top", "left bottom",
                                                                 Display._theme.background_start_color,
                                                                 Display._theme.background_end_color);
            break;
          case GradientType.Vertical:
            backgroundContent = _buildLinearGradient("left top", "right top",
                                                                 Display._theme.background_start_color,
                                                                 Display._theme.background_end_color);
            break;
          case GradientType.LeftTop:
            backgroundContent = _buildLinearGradient("left top", "right bottom",
                                                                 Display._theme.background_start_color,
                                                                 Display._theme.background_end_color);
            break;
          case GradientType.LeftBottom:
            backgroundContent = _buildLinearGradient("left bottom", "right top",
                                                                 Display._theme.background_start_color,
                                                                 Display._theme.background_end_color);
            break;
          case GradientType.Circular:
            backgroundContent = _buildRadialGradient(window.innerWidth / 2, Display._theme.background_start_color,
                                                                 Display._theme.background_end_color);
            break;
          default:
            backgroundContent = "#000";
        }
        break;
      case BackgroundType.Image:
        backgroundContent = "url('" + Display._theme.background_filename + "')";
        console.warn(backgroundContent);
        break;
      case BackgroundType.Video:
        // never actually used since background type is overridden from video to transparent in window.py
        backgroundContent = Display._theme.background_border_color;
        backgroundHtml = "<video loop autoplay muted><source src='" + Display._theme.background_filename + "'></video>";
        console.warn(backgroundHtml);
        break;
      default:
        backgroundContent = "#000";
    }
    targetElement.style.cssText = "";
    targetElement.setAttribute("data-background", backgroundContent);
    targetElement.setAttribute("data-background-size", "cover");
    if (!!backgroundHtml) {
      background.innerHTML = backgroundHtml;
    }

    // set up the main area
    if (!is_text) {
      // only transition and background for non text slides
      return;
    }
    mainStyle = {};
    if (!!Display._theme.font_main_outline) {
      mainStyle["-webkit-text-stroke"] = "" + Display._theme.font_main_outline_size + "pt " +
                                         Display._theme.font_main_outline_color;
      mainStyle["-webkit-text-fill-color"] = Display._theme.font_main_color;
    }
    // These need to be fixed, in the Python they use a width passed in as a parameter
    mainStyle.width = Display._theme.font_main_width + "px";
    mainStyle.height = Display._theme.font_main_height + "px";
    mainStyle["margin-top"] = "" + Display._theme.font_main_y + "px";
    mainStyle.left = "" + Display._theme.font_main_x + "px";
    mainStyle.color = Display._theme.font_main_color;
    mainStyle["font-family"] = Display._theme.font_main_name;
    mainStyle["font-size"] = "" + Display._theme.font_main_size + "pt";
    mainStyle["font-style"] = !!Display._theme.font_main_italics ? "italic" : "";
    mainStyle["font-weight"] = !!Display._theme.font_main_bold ? "bold" : "";
    mainStyle["line-height"] = "" + (100 + Display._theme.font_main_line_adjustment) + "%";
    // Using text-align-last because there is a <br> seperating each line
    switch (Display._theme.display_horizontal_align) {
      case HorizontalAlign.Justify:
        mainStyle["text-align"] = "justify";
        mainStyle["text-align-last"] = "justify";
        break;
      case HorizontalAlign.Center:
        mainStyle["text-align"] = "center";
        mainStyle["text-align-last"] = "center";
        break;
      case HorizontalAlign.Left:
        mainStyle["text-align"] = "left";
        mainStyle["text-align-last"] = "left";
        break;
      case HorizontalAlign.Right:
        mainStyle["text-align"] = "right";
        mainStyle["text-align-last"] = "right";
        break;
      default:
        mainStyle["text-align"] = "center";
        mainStyle["text-align-last"] = "center";
    }
    switch (Display._theme.display_vertical_align) {
      case VerticalAlign.Middle:
        mainStyle["justify-content"] = "center";
        break;
      case VerticalAlign.Top:
        mainStyle["justify-content"] = "flex-start";
        break;
      case VerticalAlign.Bottom:
        mainStyle["justify-content"] = "flex-end";
        // This gets around the webkit scroll height bug
        mainStyle["padding-bottom"] = "" + (Display._theme.font_main_size / 8) + "px";
        break;
      default:
        mainStyle["justify-content"] = "center";
    }
    if (Display._theme.hasOwnProperty('font_main_shadow_size') && !!Display._theme.font_main_shadow) {
      mainStyle["text-shadow"] = Display._theme.font_main_shadow_color + " " + Display._theme.font_main_shadow_size + "pt " +
                                 Display._theme.font_main_shadow_size + "pt";
    }
    targetElement.style.cssText = "";
    for (var mainKey in mainStyle) {
      if (mainStyle.hasOwnProperty(mainKey)) {
        targetElement.style.setProperty(mainKey, mainStyle[mainKey]);
      }
    }
    // Set up the footer
    footerStyle = {
      "text-align": "left"
    };
    footerStyle.position = "absolute";
    footerStyle.left = "" + Display._theme.font_footer_x + "px";
    footerStyle.top = "" + Display._theme.font_footer_y + "px";
    footerStyle.width = "" + Display._theme.font_footer_width + "px";
    footerStyle.height = "" + Display._theme.font_footer_height + "px";
    footerStyle.color = Display._theme.font_footer_color;
    footerStyle["font-family"] = Display._theme.font_footer_name;
    footerStyle["font-size"] = "" + Display._theme.font_footer_size + "pt";
    footerStyle["font-style"] = !!Display._theme.font_footer_italics ? "italic" : "";
    footerStyle["font-weight"] = !!Display._theme.font_footer_bold ? "bold" : "";
    footerStyle["white-space"] = Display._theme.font_footer_wrap ? "normal" : "nowrap";
    Display._footerContainer.style.cssText = "";
    for (var footerKey in footerStyle) {
      if (footerStyle.hasOwnProperty(footerKey)) {
        Display._footerContainer.style.setProperty(footerKey, footerStyle[footerKey]);
      }
    }
  },
  /**
   * Return the video types supported by the video tag
   */
  getVideoTypes: function () {
    var videoElement = document.createElement('video');
    var videoTypes = [];
    if (videoElement.canPlayType('video/mp4; codecs="mp4v.20.8"') == "probably" ||
        videoElement.canPlayType('video/mp4; codecs="avc1.42E01E"') == "pobably" ||
        videoElement.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"') == "probably") {
      videoTypes.push(['video/mp4', '*.mp4']);
    }
    if (videoElement.canPlayType('video/ogg; codecs="theora"') == "probably") {
      videoTypes.push(['video/ogg', '*.ogv']);
    }
    if (videoElement.canPlayType('video/webm; codecs="vp8, vorbis"') == "probably") {
      videoTypes.push(['video/webm', '*.webm']);
    }
    return videoTypes;
  },
  /**
   * Sets the scale of the page - used to make preview widgets scale
   */
  setScale: function(scale) {
    document.body.style.zoom = scale+"%";
  }
};
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.mediaWatcher = channel.objects.mediaWatcher;
  window.displayWatcher = channel.objects.displayWatcher;
});
