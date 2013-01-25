VHS
===

VHS is a small set of useful tools to work with 2D video tracking in HTML5 projects.

What is it for?
---

VHS will help you create advanced video effects in HTML5 known as tracking. It allows to overlay video with interactive/dynamic elements and have then follow features in the footage. The overlay elements can range from CSS to SVG, Canvas drawing or WebGL.

How does it look?
---

VHS was used on a [Tool Christmas Card](http://demo.toolprototype.com/toolxmas/), that features a 2d tracking and dynamic compositing of WebGL elements.

Video tracking was used mostly in Flash projects. Below is a list of a few of my favourite examples:

- [Take this Lollipop](http://www.takethislollipop.com/)
- [Museum of Me](http://www.intel.com/museumofme/en_US/r/index.htm)
- [Samsung Smart Park](http://www.samsungsmartpark.co.kr/)

What challenges it poses?
---

To track a video, one needs to establish the number of the frame from within code. And it needs to be done very precisely. The easiest and most straightforward way of doing this is to read the currentTime of the video and divide it by the number of frame per second. Unfortunately this is not precise enough. It wasn't precise enough in Flash and the it is the same case for HTML5 video. If you want to read how frustrating it can be there is a [great article](http://zehfernando.com/2011/flash-video-frame-time-woes/) by Zeh Fernando.

What is the workflow to make a tracking work? (short version)
---

- start with a raw video file
- use Mocha (standalone or AE plugin) to track features on the video
- export the tracking information per frame into a text file
- run the py/videomake.py script on the video file to add binary marker
- convert tracking data to JSON using py/parse_cornenrpin.py or py/parse_transform.py
- include VHS.js in your html and load the JSON with tracking data