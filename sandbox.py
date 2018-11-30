
import logging as _logging

import comedi as _comedi


MAX_SAMPLES = 128



def insn_str(insn):
    return ', '.join([
            'insn: {}'.format(insn.insn),
            'subdev: {}'.format(insn.subdev),
            'n: {}'.format(insn.n),
            'data: {!r}'.format(insn.data),
            'chanspec: {}'.format(insn.chanspec),
            ])

def setup_gtod_insn(device, insn):
    insn.insn = _comedi.INSN_GTOD
    insn.subdev = 0
    insn.n = 2
    data = _comedi.lsampl_array(2)
    data[0] = 0
    data[1] = 0
    data.thisown = False
    insn.data = data.cast()
    insn.chanspec = 0
    return insn

class SetupReadInsn (object):
    def __init__(self, subdevice, channel, range, aref, n_scan):
        self.subdevice = subdevice
        self.channel = channel
        self.range = range
        self.aref = getattr(_comedi, 'AREF_{}'.format(aref.upper()))
        self.n_scan = n_scan

    def __call__(self, device, insn):
        insn.insn = _comedi.INSN_READ
        insn.n = self.n_scan
        data = _comedi.lsampl_array(self.n_scan)
        data.thisown = False
        insn.data = data.cast()
        insn.subdev = self._get_subdevice(device)
        insn.chanspec = _comedi.cr_pack(self.channel, self.range, self.aref)
        return insn

    def _get_subdevice(self, device):
        if self.subdevice is None:
            return _comedi.comedi_find_subdevice_by_type(
                device, _comedi.COMEDI_SUBD_AI, 0);
        return self.subdevice


def setup_insns(device, insn_setup_functions):
    n = len(insn_setup_functions)
    insns = _comedi.comedi_insnlist_struct()
    insns.n_insns = n
    array = _comedi.insn_array(n)
    array.thisown = False
    for i,setup in enumerate(insn_setup_functions):
        array[i] = setup(device, array[i])
    insns.insns = array.cast()
    return insns

def free_insns(insns):
    array = _comedi.insn_array.frompointer(insns.insns)
    array.thisown = True
    for i in range(insns.n_insns):
        insn = array[i]
        data = _comedi.lsampl_array.frompointer(insn.data)
        data.thisown = True





if True:

    fname = '/dev/comedi0'
    device = _comedi.comedi_open(fname)
    if not device:
        raise Exception('error opening Comedi device {}'.format(fname))

    subdevice = 0
    channel   = 2
    aref      = 'ground'
    rng       = 0
    n_scan    = 1

    if True:
    
        setup_read_insn = SetupReadInsn(
            subdevice=subdevice, channel=channel,
            aref=aref, range=rng, n_scan=n_scan)

        insns = setup_insns(
            device, [setup_gtod_insn, setup_read_insn, setup_gtod_insn])

        ret = _comedi.comedi_do_insnlist(device, insns)
        if ret != insns.n_insns:
            raise Exception('error running instructions ({})'.format(ret))

        ret = _comedi.comedi_close(device)
        if ret != 0:
            raise Exception('error closing Comedi device {} ({})'.format(
                    args.filename, ret))

        array = _comedi.insn_array.frompointer(insns.insns)
        data = _comedi.lsampl_array.frompointer(array[1].data)
        for i in range(array[1].n):
            print(data[i])

        free_insns(insns)
