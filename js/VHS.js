VHS = function(params) {

    if (!params) params = {};

    params.readTime = params.readTime || false;

    if (!params.readTime && !params.videoWidth) throw "VHS Error. Please specify 'videoWidth' in params";
    if (!params.readTime && !params.videoHeight) throw "VHS Error. Please specify 'videoHeight' in params";
    if (params.readTime && !params.frameRate) throw "VHS Error. Please specify the video 'frameRate' in params";

    params.markerBits = params.markerBits || 16;
    params.markerBitSize = params.markerBitSize || 16;
    params.threshold = params.threshold || 128;

    if (params.readTime && params.frameRate) var samplingRate = 1 / params.frameRate;

    const colorSize = 4;

    var markerWidth = params.markerBits * params.markerBitSize;
    var markerHeight = params.markerHeight || 4;

    var markerY = params.videoHeight - markerHeight;

    var samplingLevel = markerHeight / 2 | 0;
    var samplingOffset = samplingLevel * markerWidth * colorSize;
    var samplingMid = params.markerBitSize / 2 * 4;

    var mrk = document.createElement('canvas');
    mrk.width = markerWidth;
    mrk.height = markerHeight;
    
    var ctx = mrk.getContext('2d');
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, markerWidth, markerHeight);

    this.lastFrame = 0;

    this.markerCanvas = function() {
        return mrk;
    }

    this.readFrame = function(video) {
        var f = 0;

        if (params.readTime) {
            f = Math.ceil(video.currentTime / samplingRate);
        } else {
            ctx.drawImage(video, 0, markerY, markerWidth, markerHeight, 0, 0, markerWidth, markerHeight);
            var pixels = ctx.getImageData(0, 0, markerWidth, markerHeight);

            for (var i = 0; i < params.markerBits; i++) {
                if (pixels.data[samplingOffset + i * params.markerBitSize * colorSize + samplingMid] > params.threshold) {
                    f += 1 << i;
                }
            }
        }

        f = Math.max(0, f - 1);
        this.lastFrame = f;
        return f;
    }
}