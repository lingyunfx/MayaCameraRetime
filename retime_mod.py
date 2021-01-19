from operator import itemgetter
from functools import partial
import pymel.core as pm


class DoRetime(object):

    def __init__(self, node_path, typ='Motion'):
        self.nodes = self.read_node(node_path)
        self.typ = typ
        self.st_time = int(pm.playbackOptions(query=1, minTime=1))
        self.ed_time = int(pm.playbackOptions(query=1, maxTime=1))
        self.attrs = self.get_attrs()
        self.retime_method = self.get_retime_method()

    def do_retime(self):
        objects = pm.ls(selection=True)
        if not objects:
            return pm.warning('No object Selected!')

        animation_data = {obj: self.get_keyframe_data(obj) for obj in objects}
        self.set_playback_range()

        for line in self.nodes:
            frame, linked_frame = line
            linked_frame, decimal = divmod(float(linked_frame), 1)
            for obj, attrs in animation_data.iteritems():
                pm.select(obj, r=True)
                for attr in attrs:
                    value = self.retime_method(attrs[attr], linked_frame, decimal)
                    pm.setKeyframe(v=value, t=frame, at=attr)

    def get_keyframe_data(self, obj):
        attrs = self.attrs
        if obj.getShape().type() == 'camera':
            attrs.append('fl')

        self.unlock(obj, attrs)

        frames = range(self.st_time, self.ed_time + 1)
        has_keys = partial(pm.keyframe, query=True, absolute=True)

        return {attr: {float(frame): pm.getAttr(obj.attr(attr), time=frame) for frame in frames}
                for attr in attrs if has_keys(obj.attr(attr))}

    def set_playback_range(self):
        min_frame = float(self.nodes[0][0])
        max_frame = float(self.nodes[-1][0])
        pm.playbackOptions(edit=1, minTime=min_frame)
        pm.playbackOptions(edit=1, maxTime=max_frame)
        pm.playbackOptions(edit=1, animationStartTime=min_frame)
        pm.playbackOptions(edit=1, animationEndTime=max_frame)
        pm.cutKey()

    def get_retime_method(self):
        return {'Motion': self.motion_type_method,
                'Frame': self.frame_type_method,
                'None': self.none_type_method}.get(self.typ)

    @staticmethod
    def unlock(obj, attrs):
        for attr in attrs:
            obj.attr(attr).unlock()

    @staticmethod
    def none_type_method(*args):
        values, current_frame, _ = args
        return values[current_frame]

    @staticmethod
    def frame_type_method(*args):
        values, current_frame, decimal = args
        frame = current_frame if not round(decimal) else current_frame + 1
        return values[frame]

    @staticmethod
    def motion_type_method(*args):
        values, current_frame, decimal = args
        return values[current_frame] + (values[current_frame + 1] - values[current_frame]) * decimal

    @staticmethod
    def get_attrs():
        return ['{0}{1}'.format(n, m)
                for n in ('t', 'r', 's')
                for m in ('x', 'y', 'z')]

    @staticmethod
    def read_node(node_path):
        pick_frames = itemgetter(0, 1)
        with open(node_path, 'r') as f:
            nodes = [pick_frames(n.split()) for n in f.readlines() if not n.isspace()]
        return nodes
