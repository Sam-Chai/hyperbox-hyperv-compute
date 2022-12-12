from flask import request

from . import exec_blueprint
from .instance.instance import Instance
from .util import translate_format


@exec_blueprint.route('/test', methods=('GET', 'POST'))
def test():
    return 'this is exec blueprint test'


@exec_blueprint.route('/create_instance', methods=('GET', 'POST'))
def create_instance():
    instance_name = request.args.get('instance_name')
    instance_gen = request.args.get('instance_gen')
    instance_processor = request.args.get('instance_processor')
    instance_memory = request.args.get('instance_memory')
    instance_path = request.args.get('instance_path')

    return Instance().create_instance(instance_name, instance_gen, instance_processor, instance_memory, instance_path)


@exec_blueprint.route('/delete_instance', methods=('GET', 'POST'))
def delete_instance():
    instance_name = request.args.get('instance_name')
    force = request.args.get('force')

    return Instance().delete_instance(instance_name, force)


@exec_blueprint.route('/import_instance', methods=('GET', 'POST'))
def import_instance():
    instance_name = request.args.get('instance_name')
    instance_path = request.args.get('instance_path')
    template_name = request.args.get('template_name')
    template_path = request.args.get('template_path')

    return Instance().import_instance(instance_name, instance_path, template_name, template_path)


@exec_blueprint.route('/export_instance', methods=('GET', 'POST'))
def export_instance():
    instance_name = request.args.get('instance_name')
    template_path = request.args.get('template_path')

    return Instance().export_instance(instance_name, template_path)


@exec_blueprint.route('/set_instance_power', methods=('GET', 'POST'))
def set_instance_power():
    instance_name = request.args.get('instance_name')
    action = request.args.get('action')

    return Instance().set_instance_power(instance_name, action)


@exec_blueprint.route('/create_instance_snap', methods=('GET', 'POST'))
def create_instance_snap():
    instance_name = request.args.get('instance_name')
    snap_name = request.args.get('snap_name')

    return Instance().create_instance_snap(instance_name, snap_name)


@exec_blueprint.route('/delete_instance_snap', methods=('GET', 'POST'))
def delete_instance_snap():
    instance_name = request.args.get('instance_name')
    snap_name = request.args.get('snap_name')

    return Instance().delete_instance_snap(instance_name, snap_name)


@exec_blueprint.route('/restore_instance_snap', methods=('GET', 'POST'))
def restore_instance_snap():
    instance_name = request.args.get('instance_name')
    snap_name = request.args.get('snap_name')

    return Instance().restore_instance_snap(instance_name, snap_name)


@exec_blueprint.route('/set_instance_processor', methods=('GET', 'POST'))
def set_instance_processor():
    instance_name = request.args.get('instance_name')
    processor_num = request.args.get('processor_num')
    maximum = request.args.get('maximum')
    reverse = request.args.get('reverse')
    weight = request.args.get('weight')
    extra_params = request.args.get('extra_params')
    # # translate extra_params to list format (maybe have some bug here)
    # extra_params = extra_params.replace("['", "").replace("']", "").replace("','", ",").replace("', '", ",")
    # extra_params = extra_params.replace('["', '').replace('"]', '').replace('","', ',').replace('", "', ',')
    extra_params = translate_format.trans_str_to_list(extra_params)

    return Instance().set_instance_processor(instance_name, processor_num, maximum, reverse, weight, extra_params)


@exec_blueprint.route('/set_instance_memory', methods=('GET', 'POST'))
def set_instance_memory():
    instance_name = request.args.get('instance_name')
    startup_bytes = request.args.get('startup_bytes')
    dynamic = request.args.get('dynamic')
    maximum = request.args.get('maximum')
    minimum = request.args.get('minimum')
    priority = request.args.get('priority')
    buffer = request.args.get('buffer')

    return Instance().set_instance_memory(instance_name, startup_bytes, dynamic, maximum, minimum, priority, buffer)








@exec_blueprint.route('/instance_summary', methods=('GET', 'POST'))
def instance_summary():
    instance_name = request.args.get('instance_name')

    return Instance().instance_summary(instance_name)


@exec_blueprint.route('/instance_list', methods=('GET', 'POST'))
def instance_list():
    return Instance().instance_list()


@exec_blueprint.route('/instance_snap_list', methods=('GET', 'POST'))
def instance_snap_list():
    instance_name = request.args.get('instance_name')

    return Instance().instance_snap_list(instance_name)
