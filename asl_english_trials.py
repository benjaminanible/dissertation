import expyriment as e
import cv2
from asl_english_trials import PictureNaming
from asl_english_trials.VideoInput import VideoInput

if __name__ == '__main__':
    try:
        exp = e.design.Experiment(name="Protocol 3: Picture Naming")

        for block in PictureNaming.blocks:
            exp.add_block(block)

        e.control.initialize(exp)
        exp.data_variable_names = ['picture name', 'video filename', 'type', 'reaction time']

        for block in exp.blocks:
            for trial in block.trials:
                trial.preload_stimuli()

        device = cv2.VideoCapture(0)
        device.release()

        e.control.start(exp)
        e.control.stop_audiosystem()

        for block in exp.blocks:
            for trial in block.trials:
                 trial.present_callback(trial, exp, device)
    finally:
        e.control.end(system_exit=True)
