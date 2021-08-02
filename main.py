"""Script that scans/queries info about the files from your current directory."""


import sys
import os
import json
import stat
import time



###########################################################################################################################################################################
# SCAN LOGIC
###########################################################################################################################################################################


###########################################################################################################################################################################
# Getter functions - these functions get the file attributes.

def get_file_size(file_stats):
    return file_stats.st_size

def get_last_modification(file_stats):
    year,month,day,hour,minute,_second=time.localtime(file_stats.st_mtime)[:-3]
    last_modification = "%02d/%02d/%02d-%02d:%02d"%(year,month,day,hour,minute)
    return last_modification

def get_hidden_status(file_stats_attributes):
    _hidden_status = file_stats_attributes & stat.FILE_ATTRIBUTE_HIDDEN
    hidden_status = 1 if _hidden_status == 2 else 0
    return hidden_status

def get_read_only_status(file_stats_attributes):
    read_only_status = file_stats_attributes & stat.FILE_ATTRIBUTE_READONLY
    return read_only_status

def get_all_file_attributes(file):  
    file_stats =  os.stat(file)
    file_stats_attributes = file_stats.st_file_attributes
    return [get_file_size(file_stats), get_last_modification(file_stats), get_hidden_status(file_stats_attributes), get_read_only_status(file_stats_attributes)]

###########################################################################################################################################################################
# Writing the scan results and outputing the cache.json file.

def get_scan_results():
    
    scan_results = {}
    for file in  os.listdir():
        if os.path.isfile(file):
            file_info = get_all_file_attributes(file)
            scan_results[file] = {'FileSize': file_info[0], 
                                'Changed': file_info[1], 
                                'Hidden': file_info[2], 
                                'ReadOnly' : file_info[3]}
    return scan_results

def write_json(scan_results):
    with open('cache.json', 'w') as json_cache:
        json.dump(scan_results, json_cache, indent = 4)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def scan():
    scan_results = get_scan_results()
    write_json(scan_results)


###########################################################################################################################################################################
# QUERY LOGIC
###########################################################################################################################################################################

def open_scan_results_json():
    with open('cache.json') as json_cache:
        scan_results_import = json.load(json_cache)
        return scan_results_import

###########################################################################################################################################################################
# Getter functions- analyzing the json information.

def get_nr_of_files(scan_results_import):
    nr_of_files = len(scan_results_import) 
    return nr_of_files

def get_largest_5_files(scan_results_import): 
    largest_5_files = sorted(scan_results_import, key=lambda x: scan_results_import[x]['FileSize'], reverse=True)[:5]
    return largest_5_files
 
def get_percentage_of_hidden_files(nr_of_files, scan_results_import):
    hidden_files = sum(v.get('Hidden') == 1 for v in scan_results_import.values())
    hidden_files_percentage = (hidden_files / nr_of_files) * 100 
    return hidden_files_percentage

def get_percentage_of_read_only_files(nr_of_files, scan_results_import):
    read_only_files = sum(v.get('ReadOnly') == 1 for v in scan_results_import.values())
    read_only_files_percentage = (read_only_files / nr_of_files) * 100
    return read_only_files_percentage

def get_months_with_modified_files(scan_results_import):
    months_with_modified_files = {}
    for v in scan_results_import.values():
        _date = v['Changed']
        date = _date[:7]
        months_with_modified_files[date] = months_with_modified_files.get(date,0) + 1
    
    return months_with_modified_files

def get_all_analysis_results(scan_results_import):
    nr_of_files = get_nr_of_files(scan_results_import)
    largest_files = ', '.join(map(str,get_largest_5_files(scan_results_import)))
    percentage_hidden_files = get_percentage_of_hidden_files(nr_of_files, scan_results_import)
    percentage_read_only_files = get_percentage_of_read_only_files(nr_of_files, scan_results_import)
    months_modified_files = get_months_with_modified_files(scan_results_import)

    return [nr_of_files, largest_files, percentage_hidden_files, percentage_read_only_files, months_modified_files]

###########################################################################################################################################################################
# Writing the query results.


def print_analysis_result(analysis_results):

    nr_of_files = analysis_results[0]
    largest_files = analysis_results[1]
    percentage_hidden_files = analysis_results[2]
    percentage_read_only_files = analysis_results[3]
    months_modified_files = analysis_results[4]

    print(f"Number of files: {nr_of_files}.",
            f"Top 5 largest files are : {largest_files}.",
            f"{percentage_hidden_files:.0f}% are hidden.",
            f"{percentage_read_only_files:.0f}% are read only.",
            "\n".join("{}: {} modified files.".format(k, v) for k, v in months_modified_files.items()),
            sep = '\n'
            )



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def query():
    scan_results_imported = open_scan_results_json()
    query_results = get_all_analysis_results(scan_results_imported)
    print_analysis_result(query_results)



###########################################################################################################################################################################
# TERMINAL INPUT LOGIC
###########################################################################################################################################################################


def check_cache_exists():
    return os.path.exists('cache.json')

def get_user_input():
    if len(sys.argv) == 2: 
        user_input = sys.argv[1].strip().lower()
        return user_input
    else: 
        print("Please provide 1 argument: scan/query")

def call_operation(user_input):
    if user_input in ('scan','query'):
            if user_input == 'scan':
                scan()
            else:
                if check_cache_exists():
                    query()
                else:
                    print('Never ran scan before in this directory',
                          'Running scan -> query', 
                          '\n',
                          sep= '\n')

                    scan()
                    query()
    else: 
        print("Please provide 1 argument: scan/query")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main():
    user_input = get_user_input()
    call_operation(user_input)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
    



