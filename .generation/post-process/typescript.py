#!/bin/python3

'''
Post-processing of generated code.
'''

import sys
from pathlib import Path
from typing import Generator, List
from textwrap import dedent, indent
from util import modify_file, version

INDENT = '    '

def runtime_ts(file_contents: List[str]) -> Generator[str, None, None]:
    '''Modify the runtime.ts file.'''
    for line in file_contents:
        if line.startswith('export const DefaultConfig ='):
            line = dedent(f'''\
            export const DefaultConfig = new Configuration({{
                headers: {{
                    'User-Agent': 'geoengine/openapi-client/typescript/{version("typescript")}'
                }}
            }});
            ''')

        yield line

# fixes due to https://github.com/OpenAPITools/openapi-generator/issues/14831
def project_update_token_ts(file_contents: List[str]) -> Generator[str, None, None]:
    '''Modify the ProjectUpdateToken.ts file.'''
    for line in file_contents:

        if line.startswith('export function ProjectUpdateTokenToJSON'):
            line = dedent('''\
            export function instanceOfProjectUpdateToken(value: any): boolean {
                return value === ProjectUpdateToken.None || value === ProjectUpdateToken.Delete;
            }
            ''') + '\n' + line

        yield line

# fixes due to https://github.com/OpenAPITools/openapi-generator/issues/14831
def plot_update_ts(file_contents: List[str]) -> Generator[str, None, None]:
    '''Modify the PlotUpdate.ts file.'''
    for line in file_contents:
        dedented_line = dedent(line)

        if dedented_line.startswith('return { ...PlotFromJSONTyped(json, true)'):
            line = indent(dedent('''\
            if (json === ProjectUpdateToken.None) {
                return ProjectUpdateToken.None;
            } else if (json === ProjectUpdateToken.Delete) {
                return ProjectUpdateToken.Delete;
            } else {
                return { ...PlotFromJSONTyped(json, true) };
            }
            '''), INDENT)
        elif dedented_line.startswith('if (instanceOfPlot(value))'):
            line = indent(dedent('''\
            if (typeof value === 'object' && instanceOfPlot(value)) {
            '''), INDENT)

        yield line

# fixes due to https://github.com/OpenAPITools/openapi-generator/issues/14831
def layer_update_ts(file_contents: List[str]) -> Generator[str, None, None]:
    '''Modify the LayerUpdate.ts file.'''
    for line in file_contents:
        dedented_line = dedent(line)

        if dedented_line.startswith('return { ...ProjectLayerFromJSONTyped(json, true)'):
            line = indent(dedent('''\
            if (json === ProjectUpdateToken.None) {
                return ProjectUpdateToken.None;
            } else if (json === ProjectUpdateToken.Delete) {
                return ProjectUpdateToken.Delete;
            } else {
                return { ...ProjectLayerFromJSONTyped(json, true) };
            }
            '''), INDENT)
        elif dedented_line.startswith('if (instanceOfProjectLayer(value))'):
            line = indent(dedent('''\
            if (typeof value === 'object' && instanceOfProjectLayer(value)) {
            '''), INDENT)

        yield line

# Fix: interface cannot inherit union type
def task_status_with_id_ts(file_contents: List[str]) -> Generator[str, None, None]:
    '''Modify the LayerUpdate.ts file.'''
    for line in file_contents:
        dedented_line = dedent(line)

        if dedented_line.startswith('export interface TaskStatusWithId extends TaskStatus'):
            line = dedent('''\
            export type TaskStatusWithId = { taskId: string } & TaskStatus;
                          
            export interface _TaskStatusWithId /* extends TaskStatus */ {
            ''')

        yield line


input_file = Path(sys.argv[1])

if input_file.name == 'runtime.ts':
    modify_file(input_file, runtime_ts)
if input_file.name == 'ProjectUpdateToken.ts':
    modify_file(input_file, project_update_token_ts)
elif input_file.name == 'PlotUpdate.ts':
    modify_file(input_file, plot_update_ts)
elif input_file.name == 'LayerUpdate.ts':
    modify_file(input_file, layer_update_ts)
elif input_file.name == 'TaskStatusWithId.ts':
    modify_file(input_file, task_status_with_id_ts)
else:
    pass # leave file untouched

exit(0)
