from operator import itemgetter
import pymel.core as pm


def get_frames_range():
    st_time = int(pm.playbackOptions(query=1, minTime=1))
    ed_time = int(pm.playbackOptions(query=1, maxTime=1))
    return range(st_time, ed_time + 1)


def none_type_method(*args):
    values, current_frame, _ = args
    return values[current_frame]


def frame_type_method(*args):
    values, current_frame, decimal = args
    frame = current_frame if not round(decimal) else current_frame + 1
    return values[frame]


def motion_type_method(*args):
    values, current_frame, decimal = args
    result = values[current_frame]
    if decimal:
        result += (values[current_frame + 1] - values[current_frame]) * decimal
    return result


def read_node(node_path):
    """
    Read the retime node file and return the number of frames.

    :param node_path: A txt file path.
    :return: Contains a list of the number of frames before and after retime.
    For example:

    [('1001', '1001.0000000000'),
     ('1002', '1002.3257210000'),
     ('1003', '1003.6530310000')]
    """

    pick_frames = itemgetter(0, 1)
    with open(node_path, 'r') as f:
        nodes = [pick_frames(line.split()) for line in f.readlines() if not line.isspace()]
    return nodes


class CurvesRetime(object):

    def __init__(self, node_path, typ='Motion'):
        self.allow_curve = ('animCurveTL', 'animCurveTA', 'animCurveTU')
        self.nodes = read_node(node_path)
        self.frame_range = get_frames_range()
        self.retime_method = self.get_method(typ)
        self.animation_data = self.get_animation_data()

    def do_retime(self):
        pm.waitCursor(state=True)
        self.set_playback_range()

        for line in self.nodes:
            frame, linked_frame = line
            linked_frame, decimal = divmod(float(linked_frame), 1)
            self.set_curve_keyframe(frame, linked_frame, decimal)

        self.cut_key()
        pm.waitCursor(state=False)

    def get_method(self, typ):
        return {'Motion': motion_type_method,
                'Frame': frame_type_method,
                'None': none_type_method}.get(typ)

    def get_animation_data(self):
        """
        Get all animation curve data.

        :return: A Dict.
        For Example:

        {nt.AnimCurveTL(u'camera_1_translateZ'): {1001.0: -5.167882073630977,
                                                  1002.0: -5.554315975228488,
                                                 }
         nt.AnimCurveTL(u'camera1_translateY'): {1001.0: 16.77582732509819,
                                                 1002.0: 16.789793058894574,
                                                 }
        }
        """

        anim_curves = pm.ls(type=self.allow_curve)
        animation_data = {curve: self.get_keyframe_data(curve)
                          for curve in anim_curves if curve.type() in self.allow_curve}
        return animation_data

    def get_keyframe_data(self, curve):
        """
        Get the value of each frame of an animation curve.

        :param curve: A PyMel object of type animCurve.
        :return: A Dict.
        For Example:

        {1001.0: 16.77582732509819,
         1002.0: 16.789793058894574,
         1003.0: 16.806778347654824,
         1004.0: 16.826629063127495}
        """
        return {float(frame): pm.keyframe(curve, query=True, eval=True, time=frame)[0]
                for frame in self.frame_range}

    def set_playback_range(self):
        min_frame = float(self.nodes[0][0])
        max_frame = float(self.nodes[-1][0])
        pm.playbackOptions(edit=1, minTime=min_frame)
        pm.playbackOptions(edit=1, maxTime=max_frame)
        pm.playbackOptions(edit=1, animationStartTime=min_frame)
        pm.playbackOptions(edit=1, animationEndTime=max_frame)

    def set_curve_keyframe(self, frame, linked_frame, decimal):
        """
        Set keyframes for all animation curves of a specified number of frames.
        """
        for curve, values in self.animation_data.iteritems():
            value = self.retime_method(values, linked_frame, decimal)
            pm.setKeyframe(curve, time=frame, value=value)

    def cut_key(self):
        """
        Delete animations that exceed the range of frames.
        :return:
        """
        max_time = pm.playbackOptions(query=1, maxTime=1)
        for curve in self.animation_data.keys():
            last_frame = pm.findKeyframe(curve, which='last')
            while last_frame > max_time:
                pm.cutKey(curve, time=last_frame)
                last_frame = pm.findKeyframe(curve, which='last')
