"""ASL-English Translation Trials

Usage:
    asl_english_trials.py [options]

Options:
    -h, --help          show this help
    -f, --ffmpeg EXE    ffmpeg executable [default: c:/ffmpeg/bin/ffmpeg.exe]
"""

if __name__ == '__main__':
    import os, errno, sys
    from docopt import docopt

    config = docopt(__doc__)

    # ffmpeg.exe has to exist
    if not os.path.isfile(config['--ffmpeg']):
        print config['--ffmpeg'], 'does not exist'
        exit()

    # don't load the dependencies if the args are wrong
    import expyriment as e
    import cv2
    from traceback import format_exc
    import asl_english_trials as protocols

    exp = e.design.Experiment(name="Protocol 3: Picture Naming")
    exp.data_variable_names = [
        'protocol',
        'list',
        'item',
        'condition',
        'intro time',
        'reaction time',
        'output'
    ]

    output_dir = 'data/media'
    transrecog = protocols.TranslationRecognition()
    transaudio = protocols.TranslationProductionFromAudio(output_dir)
    transvideo = protocols.TranslationProductionFromVideo(output_dir)
    naming = protocols.PictureNaming(output_dir)

    device = cv2.VideoCapture(0)
    device.release()

    try:
        e.control.initialize(exp)

        for block in transrecog.blocks + transvideo.blocks + transaudio.blocks + naming.blocks:
            exp.add_block(block)

        for block in exp.blocks:
            for trial in block.trials:
                trial.preload_stimuli()
                trial.config = config

        e.control.start(exp)
        e.control.stop_audiosystem()

        for block in exp.blocks:
            for trial in block.trials:
                 trial.present_callback(trial, exp, device)
    except BaseException as ex:
        print format_exc()
    finally:
        e.control.end()

    # turn the output data file into a csv
    # (we have to keep the xpd file around because expyriment uses it to get
    # the next subject id)
    if os.path.isfile(exp.data.fullpath):
        data, headers, info, comments = e.misc.data_preprocessing.read_datafile(exp.data.fullpath)
        e.misc.data_preprocessing.write_csv_file(exp.data.fullpath+'.csv', data, headers)

    # clean up practice files
    try:
        os.remove('practice.mp3.ogg')
    except:
        pass
    try:
        os.remove('practice.avi.mpeg')
    except:
        pass
