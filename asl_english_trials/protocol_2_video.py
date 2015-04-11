import expyriment as e
from audio_io import AudioInput

class TranslationProductionFromVideo(object):
    protocol = "protocol-2-video"
    practice_items = ["gamble", "motorcycle", "rocket", "saw", "skate"]
    trial_items = {
        "odd": ["argue", "bite", "break", "camp", "carry", "climb", "comb", "count", "dig", "drink", "eat", "exercise", "fight", "haircut", "hide", "hug", "jump", "kick", "kiss", "knot", "listen", "look", "measure", "music"],
        "even": ["open", "pay", "pickup", "pour", "pray", "preach", "protest", "sew", "shoot", "sit", "sleep", "smell", "smoke", "stand", "sweep", "swim", "telephone", "think", "turn", "violin", "vomit", "wash", "win", "write"]
    }

    def __init__(self):
        e.design.randomize.shuffle_list(self.practice_items)
        e.design.randomize.shuffle_list(self.trial_items['odd'])
        e.design.randomize.shuffle_list(self.trial_items['even'])

        self.blocks = [
            self.intro(),
            self.practice(),
            self.intermission(),
            self.trial(),
            self.finish()
        ]

    def intro(self):
        block = e.design.Block('Translation production from video: Intro')

        trial = e.design.Trial()
        intro = """
        In this task, you will view a sign in ASL.

        When you are ready, please translate the sign to English as quickly and accurately as you can.

        First, let's try some practice trials. Press enter to continue.
        """
        trial.add_stimulus(e.stimuli.TextBox(intro, (640, 240), text_justification=0))
        trial.present_callback = present_intro

        block.add_trial(trial)

        return block

    def practice(self):
        block = e.design.Block('Translation production from video: Practice')

        for item in self.practice_items:
            trial = e.design.Trial()

            trial.set_factor('item', item)
            trial.present_callback = present_practice

            space_bar = """
            Press enter to view the ASL sign.

            When you are ready, translate the sign into English. (You don't need to wait for the video to stop playing!)
            """
            trial.add_stimulus(e.stimuli.TextBox(space_bar, (640, 240), text_justification=0))
            trial.add_stimulus(e.stimuli.Video('stimuli/practice/' + item + '.mpeg1'))
            trial.add_stimulus(e.stimuli.TextLine("Press enter to continue"))

            trial.add_stimulus(e.stimuli.TextLine("For reference, here's the kind of word we're looking for..."))
            trial.add_stimulus(e.stimuli.TextLine(item.capitalize()))
            trial.add_stimulus(e.stimuli.TextLine("...and here's what you recorded. Press enter to continue."))

            block.add_trial(trial)

        return block

    def intermission(self):
        block = e.design.Block('Translation production from video: Intermission')

        trial = e.design.Trial()
        intermission = """
        Nice job! You should be ready to start the real thing.

        If you are confused, or the instructions are unclear, please talk to Benjamin before you continue.

        When you are ready to start the experiment, press enter.
        """
        trial.add_stimulus(e.stimuli.TextBox(intermission, (640, 240), text_justification=0))
        trial.present_callback = present_intro

        block.add_trial(trial)

        return block

    def trial(self):
        block = e.design.Block('Translation production from video: Trial')

        for subject, items in self.trial_items.iteritems():
            for item in items:

                trial = e.design.Trial()
                trial.present_callback = present_trial

                trial.set_factor('item', item)
                trial.set_factor('subject', subject)

                trial.add_stimulus(e.stimuli.Video('stimuli/protocol-2/trial/' + item + '.mpeg1'))
                trial.add_stimulus(e.stimuli.TextLine('Press enter to continue'))
                trial.add_stimulus(e.stimuli.TextLine('Please wait...'))

                block.add_trial(trial, random_position=True)

        return block

    def finish(self):
        block = e.design.Block('Translation production from video: Finish')

        trial = e.design.Trial()
        intermission = """
        Congratulations, you've made it through this segment of the experiment!

        Feel free to get up, walk around, stretch, get some snacks.

        When you're ready, press the "up" arrow to continue.
        """
        trial.present_callback = present_finish

        block.add_trial(trial)

        return block

def present_finish(trial, exp, device):
    trial.stimuli[0].present()
    exp.keyboard.wait([e.misc.constants.K_UP])

def present_intro(trial, exp, device):
    trial.stimuli[0].present()
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

def present_practice(trial, exp, device):

    audio = AudioInput('practice')
    blank_line = e.stimuli.TextLine('')

    trial.stimuli[0].present() # press enter and watch
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])
    audio.start()

    blank_line.present() # blank
    blank_line.present() # blank
    trial.stimuli[1].present() # sample video
    while trial.stimuli[1].is_playing:
        trial.stimuli[1].update()

    trial.stimuli[2].present() # press enter to continue
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    audio.stop.set()
    filename = audio.convert(trial.config['--ffmpeg'])
    e.control.start_audiosystem()

    trial.stimuli[3].present() # for reference
    exp.clock.wait(1500)

    trial.stimuli[4].present() # sample english word
    exp.clock.wait(2000)

    e.stimuli.Audio(filename).present()
    trial.stimuli[5].present() # what you recorded
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    e.control.stop_audiosystem()

def present_trial(trial, exp, device):

    # run trials based on the subject id
    # (THIS IS SO CHEATING)
    subject = 'odd' if exp.subject % 2 else 'even'
    if trial.get_factor('subject') != subject:
        return

    blank_line = e.stimuli.TextLine('')

    audio_id = str(exp.subject) + '-' + TranslationProductionFromVideo.protocol + '-' + trial.get_factor('item')
    audio = AudioInput(audio_id)
    audio.start()

    blank_line.present() # blank
    blank_line.present() # blank
    trial.stimuli[0].present() # sample video
    while trial.stimuli[0].is_playing:
        trial.stimuli[0].update()

    trial.stimuli[1].present() # press enter to continue
    exp.keyboard.wait([e.misc.constants.K_KP_ENTER, e.misc.constants.K_RETURN])

    trial.stimuli[2].present()
    audio.stop.set()

    exp.data.add([
        TranslationProductionFromVideo.protocol,
        'list1' if trial.get_factor('subject') is 'odd' else 'list2',
        trial.get_factor('item'),
        '',
        '',
        '',
        audio.filename
    ])

    audio.stopped.wait()

