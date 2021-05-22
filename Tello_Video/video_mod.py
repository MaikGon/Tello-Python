import os
import skvideo
import skvideo.io


# Videos
class VideoOut:
    def __init__(self, output_path, extension, width, height, fps):
        dimension = '{}x{}'.format(width, height)
        self.out = (skvideo.io.FFmpegWriter('.'.join((output_path, extension)),
                                            inputdict={'-f': 'rawvideo',
                                                       '-r': str(fps),
                                                       },
                                            outputdict={
                                                '-vcodec': 'h264',  # use the h.264 codec
                                                '-pix_fmt': 'yuv420p',
                                                '-crf': '22',
                                                '-preset': 'fast',
                                                '-s': dimension,
                                                '-r': str(fps),
                                            }))


    def write_frame(self, frame):
        self.out.writeFrame(frame[:, :, ::-1])
    def close(self):
        if self.out: 
            self.out.close()
            #self.paths.rename_output()

