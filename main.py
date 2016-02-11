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
        self.inputMode = None;
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

    def _incomplete(self):
        raise NotImplementedError("Please implement this method!");

    def TEST(self):
        self.stoType = 2;
        self.inputMode = 'Excel';
        self.rcPath = "/Users/jac0320/GitHub/stoGenerator/";
        self.mpsPath = "/Users/jac0320/GitHub/stoGenerator/";
        self.outputPath = "/Users/jac0320/GitHub/stoGenerator/";
        self.refPath = "/Users/jac0320/GitHub/stoGenerator/ExampleWorkbook.xlsx";
        self.pName = "stoGTester";

    def initialize(self):
        print "Welcome!";

        user_input = raw_input();
        while user_input is not "X" and user_input is not None:
             self.stoType = raw_input();
             clear_output();


        pass


class StoGenerator(interface):
    def __init__(self):
        self.nameLength = 0
        self.distribution = [];
        # For INDEP-RHS
        self.rhsTotal = 0;
        self.rhs = [];
        self.rhsDist = [];
        # For BLOCK-DISCRETE
        self.blockTotal = 0;
        self.rowsTotal = 0; #Assuming each block having same amount of rows
        self.blockName = [];
        self.blockRowName=[]
        self.blockRowValue={}; #blockName are keys
        self.blockProbs=[];

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
        if self.stoType == 1: #DISCRETE FILE
            # Collect all random row amount
            self.rhsTotal = indicator_sheet.cell(1,4);
            # Collect all user indicated rows
            for i in range(self.rhsTotal):
                self.rhs.append(indicator_sheet.cell(i+1,0));
            # Collect all user indicated distributions
            for i in range(self.rhsTotal):
                self.rhsDist.append(indicator_sheet.cell(i+1,1))
        if self.stoType == 2: #BLOCK FILE
            #Collect total BLOCKs and total Rows
            self.blockTotal = int(indicator_sheet.cell(0,0).value);
            self.rowsTotal = int(indicator_sheet.cell(0,1).value);
            #Collect BLOCK Names
            self.blockName.append(self.blockTotal);    #keep the count in head
            for i in range(1,self.blockTotal+1):
                self.blockName.append(indicator_sheet.cell(i,0).value);
            #Collect ROW Names
            self.blockRowName.append(self.rowsTotal);
            for i in range(1,self.rowsTotal+1):
                self.blockRowName.append(indicator_sheet.cell(0,i+1).value);
            #Collect PROBS Values
            for i in range(1,self.blockTotal+1):
                self.blockProbs.append(indicator_sheet.cell(i,1).value);
            #Collect BLOCK-ROW Values
            for i in range(1,self.blockTotal+1):
                temp = [];
                for j in range(1,self.rowsTotal+1):
                    temp.append(indicator_sheet.cell(i,j+1).value);
                self.blockRowValue[self.blockName[i]] = temp;
        pass

    def _write_discrete_sto_file(self):
        # Construct File Name
        fileName = self.pName + ".sto";
        # Contruct File in Destination Location
        stoF = open(self.outputPath+fileName, 'w');
        # Write The Sto File Head
        stoF.write('STOCH          '+self.pName+'\n');
        stoF.write('INDEP          DISCRETE\n');
        for i in range(self.rhsTotal):
            for j in range(self.rhsDist[i]):
                rhsValue = self.rhsDist[i][0];
                rhsProb = self.rhsDist[i][1];
                utility.write_space(stoF,5);
                stoF.write('RHS');
                utility._write_space(stoF,7);
                stoF.write(self.rhs[i]);
                utility._write_space(stoF,7);
                stoF.write(rhsValue);
                utility._write_space(stoF,19);
                stoF.write(rhsProb);
                stoF.write('\n');
        stoF.close()

    def _write_block_sto_file(self):
        #Construct File Name
        fileName = self.pName + ".sto";
        stoF = open(self.outputPath+fileName,'w');
        # Write the Sto File Head
        stoF.write('STOCH           '+self.pName+'\n');
        stoF.write('BLOCKS          DISCRETE\n');
        # Write Block Sections
        for i in range(1,self.blockTotal+1):
            stoF.write(' BL '+str(self.blockName[i])+'    PERIOD03        '+str(self.blockProbs[i-1])+'\n');
            for j in range(1,self.rowsTotal):
                utility.write_space(stoF,5);
                stoF.write('RHS');
                utility.write_space(stoF,9);
                stoF.write(str(self.blockRowName[j]));
                utility.write_space(stoF,11);
                stoF.write(str(self.blockRowValue[self.blockName[i]][j]));
                stoF.write('\n');
        stoF.write('ENDATA');


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
                indicator_sheet = disc_sheet;
            elif self.stoType == 2:
                indicator_sheet = bloc_sheet;

            # collect User's Indication from Excel file
            self._collect_excel_user_input(indicator_sheet);

            # Write Informaiton to File with Fixed Format
            if self.stoType == 1:
                self._write_discrete_sto_file();
            elif self.stoType == 2:
                self._write_block_sto_file();

        pass

# For Testing:
stoG = StoGenerator();
stoG.TEST();
stoG.discrete_generator();




