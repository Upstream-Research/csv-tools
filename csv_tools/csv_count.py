##  Copyright (c) 2016-2017 Upstream Research, Inc.  All Rights Reserved.  ##
##  Subject to an 'MIT' License.  See LICENSE file in top-level directory  ##

## #python-3.x
## python 2 does not work due mostly to issues with csv and io modules with unicode data

help_text = (
    "CSV-COUNT tool version 20170602\n"
    "Counts CSV rows and cells\n"
    "Copyright (c) 2017 Upstream Research, Inc.  All Rights Reserved.\n"
    "\n"
    "csv-count [OPTIONS] [InputFile]\n"
    "\n"
    "OPTIONS\n"
    "    -E {E}  Input file text encoding (e.g. 'utf-8', 'windows-1252')\n"
    "    -S {S}  Input file field delimiter (default ',')\n"
    "    -W {S}  Input line terminator (default '\\r\\n')\n"
    "    --header   print a header row containing counter names\n"
    "    --cells    print cell count\n"
    "    --columns  print column count (of first row only)\n"
    "    --rows     print row count (includes header row)\n"
    "\n"
    "By default, prints rows, columns, cells, and file name as a CSV row.\n"
)

import sys
import csv
import io

from ._csv_helpers import (
    decode_delimiter_name
    ,decode_charset_name
    ,decode_newline
    )

def main(arg_list, stdin, stdout, stderr):
    in_io = stdin
    out_io = stdout
    err_io = stderr
    show_help = False
    input_file_name = None
    output_file_name = None
    input_delimiter = ','
    output_delimiter = ','
    # 'std' will be translated to the standard line break decided by csv_helpers.decode_newline
    input_row_terminator = 'std'
    output_row_terminator = 'std'
    input_charset_name = 'utf_8_sig'
    output_charset_name = 'utf_8'
    output_charset_error_mode = 'strict'  # 'strict' | 'ignore' | 'replace' | 'backslashreplace'
    input_charset_error_mode = 'strict'  # 'strict' | 'ignore' | 'replace' | 'backslashreplace'
    csv_cell_width_limit = 4*1024*1024  # python default is 131072 = 0x00020000
    input_row_start_offset = 0
    input_row_count_max = None
    output_row_count_max = None
    should_print_header_row = False
    should_print_custom_count = False
    should_print_row_count = None
    should_print_cell_count = None
    should_print_column_count = None
    # [20160916 [db] I avoided using argparse in order to retain some flexibility for command syntax]
    arg_count = len(arg_list)
    arg_index = 1
    while (arg_index < arg_count):
        arg = arg_list[arg_index]
        if (arg == "--help" 
          or arg == "-?"
          ):
            show_help = True
        elif (arg == "-o"
          or arg == "--output"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                output_file_name = arg
        elif (arg == "-E"
          or arg == "--charset-in"
          or arg == "--encoding-in"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                input_charset_name = arg
        elif (arg == "-e"
          or arg == "--charset-out"
          or arg == "--encoding-out"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                output_charset_name = arg
        elif (arg == "--charset-in-error-mode"
        ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                input_charset_error_mode = arg
        elif (arg == "--charset-out-error-mode"
        ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                output_charset_error_mode = arg
        elif (arg == "--charset-error-mode"
        ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                input_charset_error_mode = arg
                output_charset_error_mode = arg
        elif (arg == "-S"
          or arg == "--separator-in"
          or arg == "--delimiter-in"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                input_delimiter = arg
        elif (arg == "-s"
          or arg == "--separator-out"
          or arg == "--delimiter-out"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                output_delimiter = arg
        elif (arg == "-W"
          or arg == "--terminator-in"
          or arg == "--newline-in"
          or arg == "--endline-in"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                input_row_terminator = arg
        elif (arg == "-w"
          or arg == "--terminator-out"
          or arg == "--newline-out"
          or arg == "--endline-out"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                output_row_terminator = arg
        elif (arg == "--cell-width-limit"
          ):
            if (arg_index < arg_count):
                arg_index += 1
                arg = arg_list[arg_index]
                csv_cell_width_limit = int(arg)
        elif (arg == "--header"
            or arg == "--header-out"
        ):
            should_print_header_row = True
        elif (arg == "--rows"
        ):
            should_print_custom_count = True
            should_print_row_count = True
        elif (arg == "--columns"
        ):
            should_print_custom_count = True
            should_print_column_count = True
        elif (arg == "--cells"
        ):
            should_print_custom_count = True
            should_print_cell_count = True
        elif (None != arg
          and 0 < len(arg)
          ):
            if (None == input_file_name):
                input_file_name = arg
        arg_index += 1

    if (show_help):
        out_io.write(help_text)
    else:
        if (True == should_print_custom_count):
            if (None == should_print_row_count):
                should_print_row_count = False
            if (None == should_print_column_count):
                should_print_column_count = False
            if (None == should_print_cell_count):
                should_print_cell_count = False
        else:
            should_print_row_count = True
            should_print_column_count = True
            should_print_cell_count = True

        input_charset_name = decode_charset_name(input_charset_name)
        output_charset_name = decode_charset_name(output_charset_name)
        input_row_terminator = decode_newline(input_row_terminator)
        output_row_terminator = decode_newline(output_row_terminator)
        input_delimiter = decode_delimiter_name(input_delimiter)
        output_delimiter = decode_delimiter_name(output_delimiter) 
        in_file = None
        out_file = None
        try:
            read_text_io_mode = 'rt'
            #in_newline_mode = ''  # don't translate newline chars
            in_newline_mode = input_row_terminator
            in_file_id = input_file_name
            in_close_file = True
            if (None == in_file_id):
                in_file_id = in_io.fileno()
                in_close_file = False
            in_io = io.open(
                 in_file_id
                ,mode=read_text_io_mode
                ,encoding=input_charset_name
                ,newline=in_newline_mode
                ,errors=input_charset_error_mode
                ,closefd=in_close_file
                )
            if (in_close_file):
                in_file = in_io

            write_text_io_mode = 'wt'
            out_newline_mode=''  # don't translate newline chars
            #out_newline_mode = output_row_terminator
            out_file_id = output_file_name
            out_close_file = True
            if (None == out_file_id):
                out_file_id = out_io.fileno()
                out_close_file = False
            out_io = io.open(
                 out_file_id
                ,mode=write_text_io_mode
                ,encoding=output_charset_name
                ,newline=out_newline_mode
                ,errors=output_charset_error_mode
                ,closefd=out_close_file
                )
            if (out_close_file):
                out_file = out_io

            in_csv = csv.reader(
                in_io
                ,delimiter=input_delimiter
                ,lineterminator=input_row_terminator
                )
            out_csv = csv.writer(
                out_io
                ,delimiter=output_delimiter
                ,lineterminator=output_row_terminator
                )
            execute(
                in_csv
                ,out_csv
                ,input_file_name
                ,should_print_header_row
                ,should_print_row_count
                ,should_print_column_count
                ,should_print_cell_count
                )
        except BrokenPipeError:
            pass
        finally:
            if (None != in_file):
                in_file.close()
            if (None != out_file):
                out_file.close()

def execute(
    in_csv
    ,out_csv
    ,in_file_name
    ,should_print_header_row
    ,should_print_row_count
    ,should_print_column_count
    ,should_print_cell_count
):
    end_row = None
    
    in_column_count = 0
    in_cell_count = 0
    in_row_count = 0
    in_row = next(in_csv, end_row)
    if (end_row != in_row):
        in_column_count = len(in_row)
        in_cell_count += len(in_row)
        in_row_count += 1
        in_row = next(in_csv, end_row)
    if (should_print_row_count 
        or should_print_cell_count
    ):
        while (end_row != in_row):
            in_cell_count += len(in_row)
            in_row_count += 1
            in_row = next(in_csv, end_row)
    
    out_header_row = []
    out_row = []
    if (should_print_row_count):
        out_header_row.append("rows")
        out_row.append(str(in_row_count))
    if (should_print_column_count):
        out_header_row.append("columns")
        out_row.append(str(in_column_count))
    if (should_print_cell_count):
        out_header_row.append("cells")
        out_row.append(str(in_cell_count))
    if (None != in_file_name):
        out_header_row.append("file_name")
        out_row.append(in_file_name)

    if (should_print_header_row):
        out_csv.writerow(out_header_row)
    out_csv.writerow(out_row)


def console_main():
    main(sys.argv, sys.stdin, sys.stdout, sys.stderr)

        
if __name__ == "__main__":
    console_main()