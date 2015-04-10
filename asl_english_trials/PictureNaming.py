import expyriment as e
from VideoInput import VideoInput

protocol = "protocol-3"

def present_intro(trial, exp, device):
    trial.stimuli[0].present()
    exp.keyboard.wait()

def present_practice(trial, exp, device):

    # start the video recording early so subjects don't have to wait for
    # the camera later
    video = VideoInput(device, 'practice')
    video.mirror = True
    video.start()
    video.recording.wait()

    trial.stimuli[1].present() # hold down space
    exp.keyboard.wait([e.misc.constants.K_SPACE])

    trial.stimuli[2].present() # practice image
    trial.stimuli[0].present() # blank
    trial.stimuli[3].present(clear=False) # release space bar
    exp.keyboard.wait([e.misc.constants.K_SPACE], wait_for_keyup=True)

    trial.stimuli[4].present() # sign the image
    exp.keyboard.wait()
    video.stop.set()
    filename = video.convert(trial.config['--ffmpeg'])

    trial.stimuli[5].present() # for reference
    exp.clock.wait(1500)

    trial.stimuli[0].present() # blank
    trial.stimuli[0].present() # blank
    trial.stimuli[6].present() # play sample video
    while trial.stimuli[6].is_playing:
        trial.stimuli[6].update()
    exp.clock.wait(1000)

    trial.stimuli[7].present() # what you recorded
    exp.clock.wait(1500)
    trial.stimuli[0].present() # blank
    trial.stimuli[0].present() # blank

    playback = e.stimuli.Video(filename)
    playback.present()
    while playback.is_playing:
        playback.update()
    exp.clock.wait(1000)

def present_trial(trial, exp, device):
    start = exp.clock.stopwatch_time

    video = VideoInput(device, str(exp.subject) + '-' + protocol + '-' + trial.get_factor('item'))
    video.start()
    video.recording.wait()

    trial.stimuli[0].present() # hold down space
    exp.keyboard.wait([e.misc.constants.K_SPACE])
    space_down = exp.clock.stopwatch_time
    intro_time = space_down - start

    trial.stimuli[1].present() # show image

    exp.keyboard.wait([e.misc.constants.K_SPACE], wait_for_keyup=True)
    pressed_ms = exp.clock.stopwatch_time - space_down
    e.stimuli.TextLine('').present()

    exp.clock.wait(1500)
    trial.stimuli[2].present() # press any key
    exp.keyboard.wait()
    trial.stimuli[3].present() # processing
    video.stop.set()

    exp.data.add([
        protocol,
        trial.get_factor('item'),
        trial.get_factor('type'),
        intro_time,
        pressed_ms,
        video.filename
    ])

    video.stopped.wait()

practice = ["gamble", "motorcycle", "rocket", "saw", "skate"]
items = ["argue", "bite", "break", "camp", "carry", "climb", "comb", "count", "dig", "drink", "eat", "exercise", "fight", "haircut", "hide", "hug", "jump", "kick", "kiss", "knot", "listen", "look", "measure", "music", "open", "pay", "pickup", "pour", "pray", "preach", "protest", "sew", "shoot", "sit", "sleep", "smell", "smoke", "stand", "sweep", "swim", "telephone", "think", "turn", "violin", "vomit", "wash", "win", "write"]
e.design.randomize.shuffle_list(practice)
e.design.randomize.shuffle_list(items)

blocks = []

block = e.design.Block('Picture naming: Practice')
trial = e.design.Trial()
intro = """
In this task, you will be shown pictures of assorted activities.

Once you have identified the activity in the picture, please name it in ASL as quickly and accurately as you can.

First, let's try some practice trials. Press any key to continue.
"""
trial.add_stimulus(e.stimuli.TextBox(intro, (640, 240), text_justification=0))
trial.present_callback = present_intro
block.add_trial(trial)

for idx, item in enumerate(practice):
    trial = e.design.Trial()

    trial.set_factor('item', item)
    trial.present_callback = present_practice

    trial.add_stimulus(e.stimuli.TextLine(''))

    trial.add_stimulus(e.stimuli.TextLine('Hold down the space bar'))
    trial.add_stimulus(e.stimuli.Picture('stimuli/protocol-3/practice/' + item + '.png'))
    trial.add_stimulus(e.stimuli.TextLine('Release the space bar when you are ready to name the activity', (0, -280)))

    sign = """
    Name the activity in ASL. The camera will record you while you are signing.

    When you are finished, press any key to continue.
    """
    trial.add_stimulus(e.stimuli.TextBox(sign, (640, 240), text_justification=0))

    trial.add_stimulus(e.stimuli.TextLine("For reference, here's the kind of thing we're looking for..."))
    trial.add_stimulus(e.stimuli.Video('stimuli/practice/' + item + '.mpeg1'))
    trial.add_stimulus(e.stimuli.TextLine("...and here's what you recorded..."))

    block.add_trial(trial)

trial = e.design.Trial()
intermission = """
Nice job! You should be ready to start the real thing.

If you are confused, or the instructions are unclear, please talk to Benjamin before you continue.

When you are ready to start the experiment, press any key.
"""
trial.add_stimulus(e.stimuli.TextBox(intermission, (640, 240), text_justification=0))
trial.present_callback = present_intro
block.add_trial(trial)
blocks.append(block)

block = e.design.Block('Picture naming: Trial')
for idx, item in enumerate(items):

    trial = e.design.Trial()
    trial.present_callback = present_trial

    action_type = 'p' if idx % 2 else 'np'
    image_file = action_type + '_' + item + '.png'
    trial.set_factor('type', action_type)
    trial.set_factor('item', item)

    trial.add_stimulus(e.stimuli.TextLine('Hold down the space bar, and release it when you are ready to name the picture'))
    trial.add_stimulus(e.stimuli.Picture('stimuli/protocol-3/trial/' + image_file))
    trial.add_stimulus(e.stimuli.TextLine('Press any key to continue'))
    trial.add_stimulus(e.stimuli.TextLine('Please wait...'))

    block.add_trial(trial, random_position=True)

blocks.append(block)
