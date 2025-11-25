from moviepy.editor import TextClip
     from moviepy.config import change_settings

     # Set your ImageMagick path
     change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

     # Test creating and saving a text clip frame
     TextClip('Test', fontsize=40, color='white', size=(1280,720)).save_frame('test.png')
     print('Test successful: test.png created.')