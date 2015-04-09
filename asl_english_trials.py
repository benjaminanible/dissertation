"""ASL-English Translation Trials

Usage:
    asl_english_trials.py [options]

Options:
    -h, --help          show this help
    -f, --ffmpeg EXE    specify ffmpeg executable [default: c:/ffmpeg/bin/ffmpeg.exe]
"""

if __name__ == '__main__':
    import os
    from docopt import docopt

    config = docopt(__doc__)

    # ffmpeg.exe has to exist
    if not os.path.isfile(config['--ffmpeg']):
        print config['--ffmpeg'], 'does not exist'
        exit()

    # don't load the dependencies if the args are wrong
    import expyriment as e
    import cv2
    from asl_english_trials import PictureNaming

    try:
        exp = e.design.Experiment(name="Protocol 3: Picture Naming")

        for block in PictureNaming.blocks:
            exp.add_block(block)

        e.control.initialize(exp)
        exp.data_variable_names = ['picture name', 'video filename', 'type', 'reaction time']

        for block in exp.blocks:
            for trial in block.trials:
                trial.preload_stimuli()
                trial.config = config

        device = cv2.VideoCapture(0)
        device.release()

        e.control.start(exp)
        e.control.stop_audiosystem()

        for block in exp.blocks:
            for trial in block.trials:
                 trial.present_callback(trial, exp, device)
    finally:
        e.control.end(system_exit=True)
