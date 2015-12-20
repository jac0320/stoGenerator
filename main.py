# Project Developed for Energy Research Team in Clemson University

# This project aims to provide services to stochastic programming
import os.path
import os
import fileinput
import sys
import random
from IPython.display import clear_output
from xlrd import open_workbook
import utility

# Fetch Reference File information
# Open Excel Sheet
class interface(object):
    def __init__(self):
        self.iniFlag = 0;
        self.endFlag = 0;
        self.testFlag = 0;
        self.refPath = None;
        self.rcPath = None;
        self.mpsPath = None;
        self.outputPath = None;
        self.pName = None;
        self.inputMode = None;
        self.stoType = None;
        self.pfLength = 7;

    def incomplete(self):
        raise NotImplementedError("Please implement this method!");

    def initialize(self):
        # This is going to be the beginning of everything...
        # User Input
        # User Input Part:
        #print "Please Select Stoch File Type(Choose #):";
        #print "1.INDEP";
        #print "2.BLOCKS";
        #print "Generate sto file with (type X to quit)"

        # stoType = None;
        # while stoType != "X":
        #     stoType = raw_input();
        #     clear_output();
        #

        # print "Insert refPath:"
        # refPath = raw_input();
        # if refPath == "X":
        #     sys.exit();
        # else:
        #     clear_output();

        # print "Please insert the stoch file path, (type X to quit)"
        # stoPath = None;
        # while stoPath != "X":
        #     stoPath = raw_input("Insert Path");
        #     clear_output();
        #
        # stoName = None;
        # while stoName is None:
        #     stoName = raw_input("Insert your problem's name");
        #     clear_output();
        #
        # # Generate Target File
        # if refPath == ".":
        #     # Absolute Path in current folder
        #     f = open(str(stoName), 'w');
        # else:
        #     # User Specified Path
        #     fullStoPath = os.path.join(str(stoPath), stoName + ".sto");
        #     f = open(fullStoPath, 'w');
        # Call Class Function for Use
        pass

    def _indep_rhs_only(self):
        mainObject = StoGenerator();
        mainObject.discrete_generator();
        pass


class RCDictionary(interface):
    def __init__(self):
        self.rows = {};
        self.cols = {};

    def _collect_dictionary(self, pfLength, rcPath, pName):
        # Open Rol File
        rowF = open(rcPath+pName+'.row', 'r');
        counter = 1;
        for line in rowF:
            line = line.rstrip('\r\n');
            #ripLine = line.split('[');
            #line = ripLine[0];
            strFormat = '{0:0'+str(pfLength)+'}';
            numberStr = strFormat.format(counter);
            self.cols["R"+str(numberStr)] = line;
            counter += 1;
        # Open Col File
        colF = open(rcPath+pName+'.col', 'r');
        counter = 1;
        for line in colF:
            line = line.rstrip('\r\n');
            #ripLine = line.split('[');
            #line = ripLine[0];
            strFormat = '{0:0'+str(pfLength)+'}';
            numberStr = strFormat.format(counter);
            self.rows["C"+str(numberStr)] = line;
            counter += 1;
        # Close row/col Files
        rowF.close()
        colF.close()
        pass

    def mps_translator(self, rcPath, pfLength, mpsPath, pName):
        counter = 1;
        self._collect_dictionary(pfLength,rcPath,pName);
        mpsF = open(str(mpsPath)+str(pName)+'.mps','r');
        newMpsF = open(str(mpsPath)+str(pName)+'_Tranlsated.mps','w');
        for line in mpsF:
            for key in self.rows:
                line = line.replace(key, self.rows[key]);
            for key in self.cols:
                line = line.replace(key, self.cols[key]);
            newMpsF.write(line);
            print "Line ", counter, " Fixed..."
            counter += 1;
        mpsF.close()
        newMpsF.close()
        pass


class StoGenerator(interface):
    def __init__(self):
        self.nameLength = 0
        self.distribution = [];
        # For INDEP-RHS
        self.rhsTotal = 0;
        self.rhs = [];
        self.rhsDist = [];

    def _distribution_simulator(self):
        pass

    def _collect_excel_distribution(self,dist_sheet):
        total_dist = dist_sheet.cell(0, 2).value;
        for i in range(int(total_dist)):
            dist_dict = [];
            total_bin = dist_sheet.cell(i*2+2,0).value;
            for j in range(int(total_bin)):
                dist_dict.append([dist_sheet.cell(i*2+1,j+2).value,dist_sheet.cell(i*2+2,j+2).value]);
        self.distribution.append(dist_dict);
        pass

    def _collect_excel_user_input(self,indicator_sheet):
        # Collect User's Input from Excel file and fill them into the f
        if self.stoType == 1:
            # Collect all random row amount
            self.rhsTotal = indicator_sheet.cell(1,4);
            # Collect all user indicated rows
            for i in range(self.rhsTotal):
                self.rhs.append(indicator_sheet.cell(i+1,0));
            # Collect all user indicated distributions
            for i in range(self.rhsTotal):
                self.rhsDist.append(indicator_sheet.cell(i+1,1));
        pass

    def _write_discrete_sto_file(self):
        # Construct File Name
        fileName = self.pName + ".sto";
        # Contruct File in Destination Location
        stoF = open(self.outputPath+fileName, 'w');
        # Write The Sto File Head
        stoF.write('STOCH          '+fileName+'\n');
        stoF.write('INDEP          DISCRETE\n');
        for i in range(self.rhsTotal):
            for j in range(self.rhsDist[i]):
                rhsValue = self.rhsDist[i][0];
                rhsProb = self.rhsDist[i][1];
                self._write_space(stoF,5);
                stoF.write('RHS');
                self._write_space(stoF,7);
                stoF.write(self.rhs[i]);
                self._write_space(stoF,7);
                stoF.write(rhsValue);
                self._write_space(stoF,19);
                stoF.write(rhsProb);
                stoF.write('\n');


        # Write The Sto File Body

    def discrete_generator(self):
        if self.inputMode is 'Excel':
            # Initialization Part
            book = open_workbook(self.refPath);
            disc_sheet = book.sheet_by_name('DISCRETE');
            bloc_sheet = book.sheet_by_name('BLOCKS');
            dist_sheet = book.sheet_by_name('DISTRIBUTION');
            # Cellect Distribution Knowledge from Excel File
            self._collect_excel_distribution(dist_sheet);
            if self.stoType == 1:
                indicator_sheet = bloc_sheet;
            elif self.stoType == 2:
                indicator_sheet = disc_sheet
            # collect User's Indication from Excel file
            self._collect_excel_user_input(self,indicator_sheet);
        pass

# For Testing:
test = interface();
test.pName = "stoGTester";
test.refPath = "/Users/jac0320/GitHub/stoGenerator/ExampleWorkbook.xlsx";
test.rcPath = "/Users/jac0320/GitHub/stoGenerator/";
test.mpsPath = "/Users/jac0320/GitHub/stoGenerator/";
test.stoType = 1;


