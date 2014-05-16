#!/usr/bin/env python
import sys
import os
import math
import signal

def signal_handler(signum, frame):
    #exit on CTRL-C interrupt
    sys.exit(0)

try:
    #Ignore SIG_PIPE and don't throw exceptions on it
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal_handler)
except AttributeError:
    #Doesn't work in Windows. POSIX only.
    pass

try:
    import argparse
except:
    sys.stderr.write('Looks like you are using < Python 2.7. Please install the argparse module manually with "sudo pip install argparse" or "sudo easy_install argparse"\n')
    sys.exit(2)

version = '1.1-alpha'

class Join:
    
    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2
        self.basename1 = os.path.basename(file1)
        self.basename2 = os.path.basename(file2)

        self.column1 = 1
        self.column2 = 1
        self.delimiter1 = os.getenv('IFS', None)
        self.delimiter2 = os.getenv('IFS', None)
        self.output_delimiter = None
        self.join_separator = ' '
        self.filter_mode = False
        self.remove_duplicate = False
        self.missing_mode = False       
 
        self.file1_linenum = 0

    def parse_file1(self):
        """
        Returns: dictionary of unique column values mapped to lines 
        """

        f = None
        try:
            f = open(self.file1)
            return self.parse_f1lines(f)
        except:
            sys.stderr.write('Error reading '+self.file1+'\n')
            raise
        finally:
            if f is not None:
                f.close()

    def parse_f1lines(self, iter):

        delimiter1 = self.delimiter1
        column1 = self.column1-1
        
        f1_map = {}

        for line in iter:     #for each line in lines
            self.file1_linenum += 1

            line = line.rstrip()
            chunks = line.split(delimiter1) #split by file1 delimiter

            try:
                key = chunks[column1] #get value at column1
            except IndexError:
                #print error if the specified column doesn't exist for this line
                sys.stderr.write(self.basename1+' line '+str(self.file1_linenum)+': column missing\n')
                continue

            try:
                f1_map[key].append(line)
            except KeyError:
                f1_map[key] = [line]
        
        return f1_map

    def match(self, iter, f1_map):

        delimiter1 = self.delimiter1        
        delimiter2 = self.delimiter2
        column2 = self.column2-1
        output_delimiter = self.output_delimiter
        join_separator = self.join_separator
        remove_duplicate = self.remove_duplicate
        filter_mode = self.filter_mode
        missing_mode = self.missing_mode

        linenum = 0

        for line in iter:   #for each line in file2
            linenum += 1

            line = line.rstrip()
            chunks = line.split(delimiter2)

            try:
                key = chunks[column2]  #value at column2 on this line
            except IndexError:
                #print error if the specified column doesn't exist for this line
                sys.stderr.write(self.basename2+' line '+str(linenum)+': column missing\n')
                continue

            """
            If the output_delimiter is set then we need to replace in each line.

            We also handle the remove_duplicate flag here so it impacts what the 
            outputted line looks like.
            """
            if output_delimiter != None:
                if remove_duplicate:
                    #remove the joined column from file2's line
                    chunks.pop(column2) #remove matching column from file2 line
                    line = output_delimiter.join(chunks)
                else:
                    line = line.replace(delimiter2, output_delimiter)
            else: #output delimiter is None
                if remove_duplicate:
                    #remove the joined column from file2's line
                    chunks.pop(column2) #remove matching column from file2 line
                    line = delimiter2.join(chunks)

            del chunks
            
            if missing_mode:
                if key not in f1_map:
                    print(line)
                continue

            try:
                f1_lines = f1_map[key]  #get all the lines with this key from file1

                for f1_line in f1_lines:

                    if output_delimiter != None:
                        #if output_delimiter is set then replace file1's delimiter
                        f1_line = f1_line.replace(delimiter1, output_delimiter)

                    # if filter flag is set then we don't output lines from file2
                    if filter_mode:
                        print(f1_line)
                    else:
                        #otherwise print file1 line and then file2 line
                        print('%s%s%s' % (f1_line,join_separator,line))
            except KeyError:
                pass            

    def run(self):

        f1_map = self.parse_file1() #parse file1
        
        f = None
        try:
            f = open(self.file2)            
            self.match(f, f1_map)
        except:
            sys.stderr.write('Error reading: '+self.file2+'\n')
            raise
        finally:
            if f is not None:
                f.close()

class ZigZagJoin(Join):
    
    def __init__(self, file1, file2):
        Join.__init__(self, file1, file2)
        self.file1_linenum = 0
        self.file2_linenum = 0
        self.file1_nextline = None
        self.file2_nextline = None

    def run(self):
            
        f1 = open(self.file1)
        f2 = open(self.file2)

        delimiter1 = self.delimiter1
        delimiter2 = self.delimiter2
        column2 = self.column2-1
        output_delimiter = self.output_delimiter
        join_separaator = self.join_separator
        remove_duplicate = self.remove_duplicate
        filter_mode = self.filter_mode
        missing_mode = self.missing_mode

        f1_eof = False
        f2_eof = False
        current_key = None

        while not f1_eof:
           
            if not f1_eof:
                f1_eof, current_key, f1_lines = self.readnext_file1(f1)
            
            if not f2_eof:
                f2_eof, f2_lines = self.readnext_file2(current_key, f2)

            f2_lines_out = list()
            for (f2_line, f2_chunks) in f2_lines:
                if remove_duplicate:
                    f2_chunks.pop(column2)
                
                if output_delimiter != None:
                    f2_line = output_delimiter.join(f2_chunks)
                else: #output delimiter is None
                    if delimiter2 is None and remove_duplicate:
                        f2_line = ' '.join(f2_chunks)
                    elif delimiter2 is not None and remove_duplicate:
                        f2_line = delimiter2.join(f2_chunks)
                
                f2_lines_out.append(f2_line)


            #output matches
            for (f1_line, f1_chunks) in f1_lines:

                if output_delimiter != None:
                    f1_line = output_delimiter.join(f1_chunks)

                if filter_mode and f2_lines:
                    print(f1_line)
                    continue

                for f2_line in f2_lines_out:           
                    print('%s%s%s' % (f1_line, self.join_separator, f2_line))

        f1.close()
        f2.close()

    def readnext_file2(self, current_key, f2):
        
        lines = list()
        column2 = self.column2-1

        
        if self.file2_nextline != None:
            chunks1 = self.file2_nextline.split(self.delimiter2)
            
            try:
                f2_key = chunks1[column2]
                if f2_key == current_key:
                    lines.append((self.file2_nextline, chunks1))
                elif f2_key > current_key:
                    return False, lines
            except IndexError:
                sys.stderr.write('%s line %d: column missing\n' % (self.basename1, self.file2_linenum))
        

        eof = True
        for line1 in f2:
            self.file2_linenum += 1

            line1 = line1.strip()
            chunks = line1.split(self.delimiter2)
            
            try:
                f2_key = chunks[column2]
                if f2_key == current_key:
                    lines.append((line1, chunks))
                elif f2_key > current_key:
                    #hit key greater than file1's keys
                    self.file2_nextline = line1
                    eof = False
                    break
            except IndexError:
                 sys.stderr.write('%s line %d: column missing\n' % (self.basename1, self.file2_linenum))
                 continue
            
            
        return eof, lines

    def readnext_file1(self, f1):

        current_key = None
        lines = list()
        column1 = self.column1-1

        if self.file1_nextline != None:
            chunks = self.file1_nextline.split(self.delimiter1)
            try:
                f1_key = chunks[column1]
                if current_key == None:
                    current_key = f1_key
                    lines.append((self.file1_nextline, chunks))
                elif f1_key == current_key:
                    lines.append((self.file1_nextline, chunks))
            except IndexError:
                sys.stderr.write('%s line %d: column missing\n' % (self.basename1,self.file1_linenum))

        eof = True
        for line in f1:
            self.file1_linenum += 1

            line = line.strip()
            chunks = line.split(self.delimiter1)
            try:
                
                f1_key = chunks[column1]
                if current_key == None:
                    current_key = f1_key
                    lines.append((line, chunks))
                elif f1_key == current_key:
                    lines.append((line, chunks))
                else:
                    self.file1_nextline = line
                    eof = False  
                    break

            except IndexError:
                #print error if the specified column doesn't exist for this line
                sys.stderr.write(self.basename1+' line '+str(self.file1_linenum)+': column missing\n')
                continue

        return eof, current_key, lines
          

class MemoryEfficientJoin(Join):

    def __init__(self, file1, file2, file_chunks):
        Join.__init__(self, file1, file2)
        self.file_chunks = file_chunks

    def parse_file1(self, f, chunk_size):

        lines = f.readlines(chunk_size)
        f1_map = self.parse_f1lines(lines)
        return f1_map
    
    def run(self):
        
        file1_bytes = os.path.getsize(self.file1)
        read_size = int(math.ceil(file1_bytes/float(self.file_chunks)))

        file1_handle = open(self.file1)
        file2_handle = open(self.file2)
            
        try:

            for i in range(0, self.file_chunks):

                try:
                    f1_map = self.parse_file1(file1_handle, read_size) #parse file1
                except:
                    sys.stderr.write('Error reading '+self.file1+'\n')
                    raise

                try:
                    file2_handle.seek(0)
                    self.match(file2_handle, f1_map)
                except:
                    sys.stderr.write('Error reading '+self.file2+'\n')
                    raise
        except:
            sys.stderr.write('Error reading '+self.file1+'\n')
            raise
        finally:
            file1_handle.close()
            file2_handle.close()

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
    parser.add_argument('-d1', '--delimiter1', default=[os.getenv('IFS', None)], nargs=1, 
                        help='Delimiter for file 1 (default: IFS environment variable else " ")')
    parser.add_argument('-d2', '--delimiter2', default=[os.getenv('IFS', None)], nargs=1, 
                        help='Delimiter for file 2 (default: IFS environment variable else " ")')
    parser.add_argument('-o', '--output-delimiter', nargs=1,
                        help='Output delimiter. Default is to leave delimiters for each file in place.')
    parser.add_argument('-s', '--join-separator', nargs=1, 
                        help='Separator between joined lines. This will be set to --output-delimiter if not overridden. (default: " ")')
    parser.add_argument('-f', '--filter-mode', action='store_true', 
                        help='Only output matches from file1 (default: off)')
    parser.add_argument('--missing-mode', action='store_true',
                        help='Only print column values in file2 that are not in file1 (default: off)')
    parser.add_argument('-r', '--remove-duplicate', action='store_true', help='Only output one of the matching columns (default: off)')
    parser.add_argument('-M', '--memory-efficient', action='store_true', help='Use the memory efficient implementation. (default: off)')
    parser.add_argument('-B', '--file-blocks', nargs=1, type=int, default=[50], 
                        help='Process file1 in N separate chunks. This option is ignored if not used with -M/--memory-efficient. (default: 50)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)

    args = parser.parse_args()

    if not validate_args(args):
        #exit if command line arg values are not valid
        sys.exit(1)

    file1 = args.file1[0]
    file2 = args.file2[0]

    if args.memory_efficient:
        #file_blocks = args.file_blocks[0]
        #join = MemoryEfficientJoin(file1, file2, file_blocks)
        join = ZigZagJoin(file1, file2)
    else:
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
    join.missing_mode = args.missing_mode
    join.remove_duplicate = args.remove_duplicate

    join.run()  #begin processing
