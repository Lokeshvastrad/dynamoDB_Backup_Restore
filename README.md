# DynamoDB recovery tool

This tool is a collection of Boto3 AWS tools written in Python to create and restore DynamoDB backups. 

## Getting Started

These instructions will get you a copy of the tool up and running on your local machine. 

### Prerequisites

What things you need to install the software and how to install them

* [Python 3](https://www.python.org/getit/) - The script language used
* [Boto3](https://github.com/boto/boto3) - (AWS) Software Development Kit (SDK) for Python
* AWS Credentials

### Installing

A step by step guide that tell you how to get this tool running

Python3 and Boto3 installation

Mac

```
python3 - brew install python3
boto3 - pip3 install boto3
```

Windows

```
python3 - https://docs.python-guide.org/starting/install3/win/ 
boto3 - https://github.com/boto/boto3
```

python --version

## Running the tool

PreRequisites:

* Set New MFA Token
* Assume the required AWS Role
* The script takes the region as argument

python3 dynamodb_backup_restore aws-region

eg: python3 dynamodb_backup_restore us-west-2


The script enables you to perform following operations,

* Backup - This option is used to take backup of any DynamoDB table. The Backup file will be named as TableName-Backup-YYYY-MM-DD-HH-MM.
* Restore_to_new_table - This option restores an existing Backup to a new table. The Target Table Name is same as the Backup Name.The source Table for the backup selected exists in this scenario.
* Restore_to_same_table - This option restores the selected Backup to the Table with the same name. Since we cannot have 2 Tables with the same name, it prompts for the user to confirm the deletion of the Table beforing restoring. It checks for available backups before deleting the Table. If there are no backups available then it warns the user to take backup first before using this option.
* Restore_from_point_in_time - This option is used to restore the Backup of a Table to a specific point in time to debug or re-produce any issues. In this scenario the user has to input the option from which the restore has to be done,
    * Latest: Restores the latest available backup.
    * Custom: User has to input a custom date and time in the format, YYYY,MM,DD,HH,MM.
* Restore_from_backup_when_table_does_not_exists - This option is handy when you want to restore the Backup of a Table which does not exists. In this scenario since the Table does not exists, user has to input the Table Name to list the available Backups.


```

    Args:
        [0] Backup: 
            a. Lists the available DynamoDB Tables.
            b. Takes the DynamoDB Table Number to backup (BackupName: "TableName-Backup-YYYY-MM-DD-HH-MM").
            c. Prints the backup response.
        [1] Restore_to_new_table: 
            a. Lists the available DynamoDB Tables.
            b. Takes the user input of the DynamoDB Table Number to restore from.
            c. Lists the backups available for the selected Table.
            d. Restores the selected Backup to a new table (TableName: $BackupName).
        [2] Restore_to_same_table: 
            a. Lists the available DynamoDB Tables.
            b. Takes the user input of the DynamoDB Table Number to restore. 
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

```
