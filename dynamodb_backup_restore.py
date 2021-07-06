#!/usr/bin/env python3
import os
import boto3
import datetime
import time
from timeit import default_timer as timer
import itertools, sys
                         
header = "\
 ______   __   __  __    _  _______  __   __  _______  ______   _______ \n\
|      | |  | |  ||  |  | ||   _   ||  |_|  ||       ||      | |  _    |\n\
|  _    ||  |_|  ||   |_| ||  |_|  ||       ||   _   ||  _    || |_|   |\n\
| | |   ||       ||       ||       ||       ||  | |  || | |   ||       |\n\
| |_|   ||_     _||  _    ||       ||       ||  |_|  || |_|   ||  _   | \n\
|       |  |   |  | | |   ||   _   || ||_|| ||       ||       || |_|   |\n\
|______|   |___|  |_|  |__||__| |__||_|   |_||_______||______| |_______|\n"

colors = {
        'blue': '\033[94m',
        'pink': '\033[95m',
        'green': '\033[92m',
        }
 
tables=[]
backup_list=[]
backup_Arn=[]
restore_same_table_flag=False
restore_from_backup_no_table_flag=False
restore_from_backup_flag=False

dynamodb_client = boto3.client('dynamodb')
list_backup_paginator = dynamodb_client.get_paginator('list_backups')


def colorize(string, color):
    if not color in colors: return string
    return colors[color] + string + '\033[0m'


# Function to list the DynamoDB tables
def list_tables():
    client = boto3.client('dynamodb', sys.argv[1])
    response = client.list_tables()
    for key in response['TableNames']:
        tables.append(key)
    i=0
    for item in tables:
        print (colorize("[" + str(i) + "] ", 'blue') + item)
        i+=1


# Function to take the backup of a Table
def createbackup():
    print("Enter the table number")
    choice_table = input(">> ")
    try:
        if int(choice_table) < 0 : raise ValueError
        print("you selected", tables[int(choice_table)])
        response = dynamodb_client.create_backup(
        TableName=tables[int(choice_table)],
        BackupName=tables[int(choice_table)]+'-Backup-'+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")  
    
    )
    except (ValueError, IndexError):
        pass
    print(response)
    print("\nBackup is created\n")


# Function to delete the table when restore to same table option is selected
def deleteTable(table_to_delete):
    response = dynamodb_client.delete_table(
    TableName = table_to_delete
)
    # spinner = itertools.cycle(['-', '/', '|', '\\'])
    print("Deleting Table",table_to_delete )
    # waiter function to wait until the table is deleted
    waiter = dynamodb_client.get_waiter('table_not_exists')
    waiter.wait(
    TableName=table_to_delete,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 10
    }
)
    print("Deleted table", table_to_delete)


# Function to get the ARN of the backup selected
def backupArn(selected_table_to_restore,selected_backup):
    responseArn = list_backup_paginator.paginate(
        TableName=selected_table_to_restore,
    )
    for result in responseArn:
        if "BackupSummaries" in result:
            for names in result["BackupSummaries"]:
                if (names['BackupName'] ==  selected_backup):
                    backup_Arn.append(names['BackupArn'])

# list_backups Function
def list_backups(selected_table_to_restore):
    global target_table_name
    # backup_lower_date_time = input("Enter the TimeRangeLowerBound for BackupList in the format(YYYY,MM,DD):")
    # backup_lower_date_time_epoch = datetime.datetime.strptime(backup_lower_date_time, "%Y,%m,%d").timestamp()
    # backup_upper_date_time = input("Enter the TimeRangeUpperBound for BackupList in the format(YYYY,MM,DD):")
    # backup_upper_date_time_epoch = datetime.datetime.strptime(backup_upper_date_time, "%Y,%m,%d").timestamp()
    print("Listing Backup available for %s\n" % selected_table_to_restore)
    response = list_backup_paginator.paginate(
        TableName = selected_table_to_restore,
        # TimeRangeLowerBound=backup_lower_date_time_epoch,
        # TimeRangeUpperBound=backup_upper_date_time_epoch,
        # Limit = 100,
    )
    # for names in response['BackupSummaries']:
    #     backup_list.append(names['BackupName'])

    for result in response:
        if "BackupSummaries" in result:
            for key in result["BackupSummaries"]:
                BackupName = key["BackupName"]
                backup_list.append(BackupName)
    
    if not backup_list:
        print("No Backups Available. Please take a backup of this table before proceeding with this option")
        exit
    else:
        i=0
        for backups in backup_list:
            print(colorize("[" + str(i) + "]", 'blue') + backups)
            i+=1
        print("select the backup to restore")
        backup_choice = input(">> ")
        try:
            if int(backup_choice) < 0 : raise ValueError
            backupArn(selected_table_to_restore,backup_list[int(backup_choice)])
            print("the selected table is",selected_table_to_restore)
            print("the selected backup is", backup_list[int(backup_choice)])
        except (ValueError, IndexError):
            pass

        target_table_name = backup_list[int(backup_choice)]


# restoreBackup Function
def restoreCondition():
    if (restore_from_backup_flag == True):
        print("Enter the table number to restore from")
        choice_table_restore = input(">> ")
        list_backups(tables[int(choice_table_restore)])
        # Check for existing backups of the input table before Deleting
        if not backup_list:
            exit
        else:
            restoreBackup(target_table_name)

    elif (restore_from_backup_no_table_flag == True):
        target_table_name_no_table = input("Enter the table name to list backups:\n")
        list_backups(target_table_name_no_table)
        restoreBackup(target_table_name_no_table)

    elif (restore_same_table_flag == True):
        table_to_delete = input("To be able to restore to the same table, we need to delete the table. Are you sure you want to delete the table? If so, Enter the table name to delete:\n")
        list_backups(table_to_delete)
        if not backup_list:
            exit
        else:
            deleteTable(table_to_delete)
            restoreBackup(table_to_delete)


def restoreBackup(target_table_name):
    response = dynamodb_client.restore_table_from_backup(
        TargetTableName=target_table_name,
        BackupArn=backup_Arn[0]
    )
    print("Restore started for selected target table", target_table_name)
    print("Backup ARN is", backup_Arn[0])
    # We could use the built-in waiter function. However, sometimes the table is deleted even before the waiter run. Hence throwing an error "Table does not exists."
    # waiter = dynamodb_client.get_waiter('table_exists')
    # waiter.wait(
    # TableName=target_table_name,
    # WaiterConfig={
    #     'Delay': 30,
    #     'MaxAttempts': 20
    #     }
    # )
    spinner = itertools.cycle(['-', '/', '|', '\\']) # Spinner to wait until the restore is completed
    start = timer()
    while True:
        sys.stdout.write(next(spinner))  # write the next character
        sys.stdout.flush()                # flush stdout buffer (actual character display)
        sys.stdout.write('\b')
        response = dynamodb_client.describe_table(
            TableName = target_table_name
        )
        if(response['Table']['TableStatus'] == 'ACTIVE'):
            end = timer()
            print("The total time elapsed for the restore is: ", end - start, "seconds")
            break
    # print(response)


def restore_table_from_pitr():
    print("Enter the table number")
    choice_table = input(">> ")
    try:
        if int(choice_table) < 0 : raise ValueError
        print("you selected", tables[int(choice_table)])
        timeRange = dynamodb_client.describe_continuous_backups(
        TableName = tables[int(choice_table)]
        )
        if (restore_latest_pitr_backup_flag == 'False'):
            print("Select the Time range between EarliestRestorableDateTime", timeRange['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['EarliestRestorableDateTime'], "and LatestRestorableDateTime", timeRange['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['LatestRestorableDateTime'])
            pitr_restore_date_time = input("Enter the RestoreDateTime in the format(YYYY,MM,DD,HH,MM,SS):")
            pitr_restore_epoch = datetime.datetime.strptime(pitr_restore_date_time, "%Y,%m,%d,%H,%M,%S").timestamp() # Convert user input to epoch
            pitr_target_table_name = input("Enter the target Table name to restore point_in_time_recovery backup:")
            response = dynamodb_client.restore_table_to_point_in_time(
                SourceTableName=tables[int(choice_table)],
                TargetTableName=pitr_target_table_name,
                UseLatestRestorableTime=False,
                RestoreDateTime=(pitr_restore_epoch)
            )
        elif (restore_latest_pitr_backup_flag == 'True'):
            print("The DB will be restored to LatestRestorableDateTime", timeRange['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['LatestRestorableDateTime'])
            pitr_target_table_name = input("Enter the target Table name to restore point_in_time_recovery backup:")
            response = dynamodb_client.restore_table_to_point_in_time(
                SourceTableName=tables[int(choice_table)],
                TargetTableName=pitr_target_table_name,
                UseLatestRestorableTime=True
            )
    except (ValueError, IndexError):
        pass
    print("Restoration started...")
    # print(response)


# Menu Functions

def backup():
    print ("You called backup()")
    list_tables()
    createbackup()


def restore_from_backup():
    print ("You called restore_from_backup()")
    global restore_from_backup_flag 
    restore_from_backup_flag = True
    list_tables()
    restoreCondition()
    # print("Table Restore Completed")


def restore_to_same_table():
    print ("You called restore_to_same_table()")
    global restore_same_table_flag 
    restore_same_table_flag = True
    list_tables()
    restoreCondition()


def restore_from_backup_no_table():
    print ("You called restore_from_backup_no_table()")
    global restore_from_backup_no_table_flag
    restore_from_backup_no_table_flag = True
    restoreCondition()
    # print("Table Restore Completed")


def restore_from_point_in_time():
    print ("You called restore_from_point_in_time()")
    global restore_latest_pitr_backup_flag
    restore_latest_pitr_backup_flag = input("Do you like to restore from the latest backup? True/False\n").strip()
    list_tables()
    restore_table_from_pitr()


def help():
    print(main.__doc__)


menuItems = [
    { "Backup": backup },
    { "Restore_to_new_table": restore_from_backup },
    { "Restore_to_same_table": restore_to_same_table },
    { "Restore_from_point_in_time": restore_from_point_in_time },
    { "Restore_from_backup_when_table_does_not_exists": restore_from_backup_no_table},
    { "Help": help},
    { "Exit": exit },
]
 
def main():
    """
    This script takes user input to backup and restore DynamoDB Tables. You need to set mfa session and assume required role before executing this script.

    Args:
        [0] Backup: 
            a. Lists the available DynamoDB Tables.
            b. Takes the DynamoDB Table Number to backup (BackupName: "TableName-Backup-YYYY-MM-DD-HH-MM").
            c. Prints the backup response.
        [1] Restore_to_new_table: 
            a. Lists the available DynamoDB Tables.
            b. Takes the DynamoDB Table Number to restore from.
            c. Lists the backups available for the selected Table.
            d. Restore the selected Backup to a new table (TableName: $BackupName).
        [2] Restore_to_same_table: 
            a. Lists the available DynamoDB Tables.
            b. Takes the DynamoDB Table Number to restore. 
            c. Asks for User Confirmation to delete the source Table and deletes the table.
            d. Lists the available Backups of the selected Table.
            e. Restores the selected Backup to the table with same name.
        [3] Restore_from_point_in_time:
            a. Asks for the User Input: Do you like to restore from the latest backup? True/False
            b. Lists the available DynamoDB Tables. 
            c. Based on the selected option from a, asks user for the Target Table and Point In Time Restore Value.
        [4] Restore_from_backup_when_table_does_not_exists
            a. Asks for User Input to enter the source Table Name. 
            b. Lists the available Backups of the selected Table.
            c. Restores the selected Backup to the table with same name.
        [5] Help:
            a. shows help
        [6] exist:
            a. Exits the script

    Returns:
        Returns the response of the selected operation.

    Raises:
        ValueError: Raises a Value Exception.
        IndexError: Raises an Index Exception.

    """
    print (colorize(header, 'pink'))
    while True:
        # os.system('clear')
        # print (colorize('version 0.1\n', 'green'))
        for item in menuItems:
            print (colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + list(item.keys())[0])
        choice = input(">> ")
        del tables[:] # Empty the table list for each selection
        del backup_list[:] # Empty the backup_list list for each selection
        try:
            if int(choice) < 0 : raise ValueError
            list(menuItems[int(choice)].values())[0]()
        except (ValueError, IndexError):
            pass
 
if __name__ == "__main__":
    main()

