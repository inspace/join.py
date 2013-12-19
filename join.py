#!/usr/bin/env python
import sys
import os

try:
    import argparse
except:
    sys.stderr.write('Looks like you are using < Python 2.7. Please install the argparse module manually with "sudo pip install argparse" or "sudo easy_install argparse"\n')
    sys.exit(2)

version='1.0'

class Join:
    
    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2
        self.basename1 = os.path.basename(file1)
        self.basename2 = os.path.basename(file2)

        self.column1 = 1
        self.column2 = 1
        self.delimiter1 = ' '
        self.delimiter2 = ' '
        self.output_delimiter = None
        self.join_separator = ' '
        self.filter_mode = False
        self.remove_duplicate = False

    def parse_file1(self):
        """
        Returns: dictionary of unique column values mapped to lines 
        """

        f1_map = {}

        f = None
        try:
            f = open(self.file1)
            linenum = 0
            for line in f:     #for each line in file1
                linenum += 1

                line = line.strip()
                chunks = line.split(self.delimiter1) #split by file1 delimiter

                if len(chunks) < self.column1:   
                    #print error if the specified column doesn't exist for this line
                    sys.stderr.write(self.basename1+' line '+str(linenum)+': column missing\n')
                    continue

                key = chunks[self.column1-1] #get value at column1
    
                if key not in f1_map:        #initialize list to hold lines for this key
                    f1_map[key] = list()
    
                f1_map[key].append(line)
        except:
            sys.stderr.write('Error reading '+self.file1+'\n')
            raise
        finally:
            if f is not None:
                f.close()

        return f1_map

    def run(self):
        
        f1_map = self.parse_file1() #parse file1

        f = None
        try:
            f = open(self.file2)
            linenum = 0
            for line in f:   #for each line in file2
                linenum += 1

                line = line.strip()
                chunks = line.split(self.delimiter2)
    
                if len(chunks) < self.column2:
                    #print error if the specified column doesn't exist for this line
                    sys.stderr.write(self.basename2+' line '+str(linenum)+': column missing\n')
                    continue

                key = chunks[self.column2-1]  #value at column2 on this line


                """
                If the output_delimiter is set then we need to replace in each line.

                We also handle the remove_duplicate flag here so it impacts what the 
                outputted line looks like.
                """
                if self.output_delimiter != None:
                    if self.remove_duplicate:
                        #remove the joined column from file2's line
                        chunks.pop(self.column2-1) #remove matching column from file2 line
                        line = self.output_delimiter.join(chunks)
                    else:
                        line = line.replace(self.delimiter2, self.output_delimiter)
                else: #output delimiter is None
                    if self.remove_duplicate:
                        #remove the joined column from file2's line
                        chunks.pop(self.column2-1) #remove matching column from file2 line
                        line = self.delimiter2.join(chunks)


                
                if key in f1_map: #if key from file2 is in file1 then join these
                
                    f1_lines = f1_map[key]  #get all the lines with this key from file1
                    for f1_line in f1_lines:

                        if self.output_delimiter != None:
                            #if output_delimiter is set then replace file1's delimiter
                            f1_line = f1_line.replace(self.delimiter1, self.output_delimiter)

                        # if filter flag is set then we don't output lines from file2
                        if self.filter_mode: 
                            print(f1_line)
                        else:
                            #otherwise print file1 line and then file2 line
                            print(f1_line+self.join_separator+line)
        except:
            sys.stderr.write('Error reading: '+self.file2+'\n')
            raise
        finally:
            if f is not None:
                f.close()

def validate_args(args):
    """
    Perform basic validation on command line arguments
    """

    if args.column1[0] < 1 or args.column2[0] < 1:
        sys.stderr.write('Error: Valid column values are >= 1\n')
        return False

    file1 = args.file1[0]
    file2 = args.file2[0]

    if not os.path.exists(file1):
        sys.stderr.write('Error: '+file1+' does not exist\n')
        return False
    if os.path.isdir(file1):
        sys.stderr.write('Error: '+file1+' is a directory\n')
        return False
    if not os.path.exists(file2):
        sys.stderr.write('Error: '+file2+' does not exist\n')
        return False
    if os.path.isdir(file2):
        sys.stderr.write('Error: '+file2+' is a directory\n')
        return False

    return True

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Join two files.')
    parser.add_argument('file1', nargs=1, help='Path to file 1')
    parser.add_argument('file2', nargs=1, help='Path to file 2')
    parser.add_argument('-c1', '--column1', type=int, default=[1], nargs=1, 
                        help='Column number for file 1 (default: 1)')
    parser.add_argument('-c2', '--column2', type=int, default=[1], nargs=1, 
                        help='Column number for file 2 (default: 1)')
    parser.add_argument('-d1', '--delimiter1', default=[' '], nargs=1, 
                        help='Delimiter for file 1 (default: " ")')
    parser.add_argument('-d2', '--delimiter2', default=[' '], nargs=1, 
                        help='Delimiter for file 2 (default: " ")')
    parser.add_argument('-o', '--output-delimiter', nargs=1,
                        help='Output delimiter. Default is to leave delimiters for each file in place.')
    parser.add_argument('-s', '--join-separator', nargs=1, 
                        help='Separator between joined lines. This will be set to --output-delimiter if not overridden. (default: " ")')
    parser.add_argument('-f', '--filter-mode', action='store_true', 
                        help='Only output matches from file1 (default: off)')
    parser.add_argument('-r', '--remove-duplicate', action='store_true', help='Only output one of the matching columns (default: off)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)

    args = parser.parse_args()

    if not validate_args(args):
        #exit if command line arg values are not valid
        sys.exit(1)

    file1 = args.file1[0]
    file2 = args.file2[0]

    join = Join(file1, file2)

    join.column1 = args.column1[0]
    join.column2 = args.column2[0]

    join.delimiter1 = args.delimiter1[0]
    join.delimiter2 = args.delimiter2[0]

    join.output_delimiter = None if args.output_delimiter is None else args.output_delimiter[0]
    
    #if output-delimiter is set and join_delimiter
    if join.output_delimiter is not None and args.join_separator is None:
        join.join_separator = join.output_delimiter
  
    if args.join_separator is not None:
        join.join_separator = args.join_separator[0]

    join.filter_mode = args.filter_mode
    join.remove_duplicate = args.remove_duplicate

    join.run()  #begin processing
