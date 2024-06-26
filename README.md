# DiffDuck

This repository contains all the necessary files to run DiffDuck simulations along with the programs to reproduce the results in (link to DiffDuck paper?).

## Table of contents

## Requirements

## Contains

## Install

## Execution

## Results

## Reproduce figures

First clone the directory containing all the necessary files by doing:

```bash
git clone https://github.com/Albert2424/DiffDuck.git
```
Then move to the downloaded directory inside `DB_example` and use `source start.sh` to generate all the required directories for the code to work. This will also display a help for running the program. To reproduce all the work use `diffduck run`. 

**_NOTE:_** _to reproduce the figures the `fails_solo.csv` file is needed. If this feature is not needed just change the `f` variable in `input.dat` for `None` and run the program._ 

### How does this code work?

The code is split into three main parts. The first part consists of cleaning the selected database (in the example is `Database_example.zip` which is automatically unzipped when you run the code). After running `DB_cleanning.py` from the `/codes` directory, the following files are generated inside the `/output` directory:


1. `AF_input.csv`       --> In case you don't have the PDB structure of the studied proteins, it may be useful to run a structure predictor program (such as AlphaFold) to obtain them. This file is a valid input for Colabfold_batch (AlphaFold, DeepFold).

||id   |sequence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|------|-----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|0     |'0'  |AVPFVEDWDLVQTLGEGAYGEVQLAVNRVTEEAVAVKIVDMKRAVDCPENIKKEICINKMLNHENVVKFYGHRREGNIQYLFLEYCSGGELFDRIEPDIGMPEPDAQRFFHQLMAGVVYLHGIGITHRDIKPENLLLDERDNLKISDFGLATVFRYNNRERLLNKMCGTLPYVAPELLKRREFHAEPVDVWSCGIVLTAMLAGELPWDQPSDSCQEYSDWKEKKTYLNPWKKIDSAPLALLHKILVENPSARITIPDIKKDRWYNKPLKKGAKRPRVTS                                                                                                                                                                                                                     |
|1     |'1'  |GEAGRDGMGDTGRDSRSPDSSSPNPLSQGIPPSSPPGPPHTPSAPPPPMPPPPLGSPFPVISSSMGSPGLPPPAPPGFSGPVSSPQINSTVSLPGGGSGPPEDVKPPVLGVRGLHCPPPPGGPGAGKRLCAICGDRSSGKHYGVYSCEGCKGFFKRTIRKDLTYSCRDNKDCTVDKRQRNRCQYCRYQKCLATGMKREAVQEERQRGKDKDGDGDGAGGAPEEMPVDRILEAELAVEQKSDQGVEGPGATGGGGSSPNDPVTNICQAADKQLFTLVEWAKRIPHFSSLPLDDQVILLRAGWNELLIASFSHRSIDVRDGILLATGLHVHRNSAHSAGVGAIFDRVLTELVSKMRDMRMDKTELGCLRAIILFNPDAKGLSNPGEVEILREKVYASLETYCKQKYPEQQGRFAKLLLRLPALRSIGLKCLEHLFFFKLIGDTPIDTFLMEMLEAPHQLA                                  |
|2     |'11' |MANPLHLVLLGAALAGLLLSGSSVFISRRAANDVLARTRRANSFLEELKKGNLERECMEENCSYEEALEVFEDREKTNEFWNKYVDGDQCESNPCQNQGTCKDGLGMYTCSCVEGYEGQDCEPVTRKLCSLDNGGCDQFCKEEENSVLCSCASGYTLGDNGKSCISTELFPCGKVTLGRWRRSPATNSSEGPPEAPGPEQQDDGNLTATENPFNLLDSPEPPPEDDSSSLVRIVGGQDCRDGECPWQALLVNEENEGFCGGTILSEYHVLTAAHCLHQAKRFKVRVGDRDTEHEEGNEETHEVEVVVKHNRFVKETYDFDIAVLRLKTPITFRRNVAPACLPQKDWAESTLMAQKTGIVSGFGRTHEMGRLSTTLKMLEVPYVDRNSCKRSSSFTITQNMFCAGYDARPEDACQGDSGGPHVTRFRDTYFVTGIVSWGEGCARKGKFGVYTKVSNFLKWIEKSMRARAVPVAEAAGTPGPTQPTIKGSPS  |
|...|...|...|

2. `data_prot.csv`      --> Contains the selected data from the database (i.e. all data that has a valid $K_i$ value). In this data, you may encounter sequences used in the DiffDock training so you may consider excluding them.

||BindingDB Target Chain Sequence|PubChem CID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |ki_mean             |ki_sem               |SMILES                                                                                                                                                                                         |ID |
|------|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
|0     |AVPFVEDWDLVQTLGEGAYGEVQLAVNRVTEEAVAVKIVDMKRAVDCPENIKKEICINKMLNHENVVKFYGHRREGNIQYLFLEYCSGGELFDRIEPDIGMPEPDAQRFFHQLMAGVVYLHGIGITHRDIKPENLLLDERDNLKISDFGLATVFRYNNRERLLNKMCGTLPYVAPELLKRREFHAEPVDVWSCGIVLTAMLAGELPWDQPSDSCQEYSDWKEKKTYLNPWKKIDSAPLALLHKILVENPSARITIPDIKKDRWYNKPLKKGAKRPRVTS|3653116.0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |17200.0             |0.0                  |Clc1ccc2Nc3ccccc3C(=O)Nc2c1                                                                                                                                                                    |0  |
|1     |AVPFVEDWDLVQTLGEGAYGEVQLAVNRVTEEAVAVKIVDMKRAVDCPENIKKEICINKMLNHENVVKFYGHRREGNIQYLFLEYCSGGELFDRIEPDIGMPEPDAQRFFHQLMAGVVYLHGIGITHRDIKPENLLLDERDNLKISDFGLATVFRYNNRERLLNKMCGTLPYVAPELLKRREFHAEPVDVWSCGIVLTAMLAGELPWDQPSDSCQEYSDWKEKKTYLNPWKKIDSAPLALLHKILVENPSARITIPDIKKDRWYNKPLKKGAKRPRVTS|10003686.0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |5.79                |0.0                  |COc1cc(ccc1[N+]([O-])=O)-c1ccc2c(Nc3ccc(CC(=O)N(C)C)cc3NC2=O)c1                                                                                                                                |0  |
|...|...|...|...|...|...|...|

Here the code needs a file of the result from BLASTp, comparing the aminoacid sequence of the proteins with the _PDB_ database. The proteins with a identity score of 100% with the proteins in the _PDBBind_ database will be excluded. To compere the result from the BLAST, is necesary to download the _Hit table(csv)_ results and run `compare_PDBbind.sh`. In order to work, this code needs the PDB codes from the _PDBBind_ database `2020_index.lst`, a list you can donwload from the database website. In case the user doesn't want to exclude said proteins, just comment the `drop_if_in_training('pdbbind_match_example.csv',df)` line of the `DB_cleanning.py` code. In the other case, a file with a format like _pdbbind_match_example.csv_: 


|0  |
|---|
|1  |
|2  |
|3  |
|4  |
|...  |



where the only column it contains are the indices of the rows to drop will be needed. Whichever is decision taken, the following files will be generated:

3. `data_A.csv`         --> Paired with data_B.csv will provide the different pairs of competing proteins for every ligand.

4. `data_B.csv`

  ||Prot ID|Sequence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |SMILES              |Ki (nM)              |ki SEM                                                                                                                                                                                         |PubChem CID|
|------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
|0     |174    |PQITLWQRPFVTIKIEGQLKEALLDTGADDTVLEEMNLPGRWKPKMIGGIGGFIKVRQYDQIVIEICGKKAIGTVLVGPTPVNIIGRNLLTQIGCTLNF                                                                                                                                                                                                                                                                                                                                                                                                         |CC(C)(C)NC(=O)[C@@H]1CN(Cc2cccnc2)CCN1C[C@@H](O)C[C@@H](Cc1ccccc1)C(=O)N[C@@H]1[C@H](O)Cc2ccccc12|0.4438               |0.034173674078155546                                                                                                                                                                           |5362440.0  |
|1     |174    |PQITLWQRPFVTIKIEGQLKEALLDTGADDTVLEEMNLPGRWKPKMIGGIGGFIKVRQYDQIVIEICGKKAIGTVLVGPTPVNIIGRNLLTQIGCTLNF                                                                                                                                                                                                                                                                                                                                                                                                         |CC(C)(C)NC(=O)[C@@H]1CN(Cc2cccnc2)CCN1C[C@@H](O)C[C@@H](Cc1ccccc1)C(=O)N[C@@H]1[C@H](O)Cc2ccccc12|0.4438               |0.034173674078155546                                                                                                                                                                           |5362440.0  |
|2     |174    |PQITLWQRPFVTIKIEGQLKEALLDTGADDTVLEEMNLPGRWKPKMIGGIGGFIKVRQYDQIVIEICGKKAIGTVLVGPTPVNIIGRNLLTQIGCTLNF                                                                                                                                                                                                                                                                                                                                                                                                         |CC(C)(C)NC(=O)[C@@H]1CN(Cc2cccnc2)CCN1C[C@@H](O)C[C@@H](Cc1ccccc1)C(=O)N[C@@H]1[C@H](O)Cc2ccccc12|0.4438               |0.034173674078155546                                                                                                                                                                           |5362440.0  |
|...|...|...|...|...|...|...|

5. `clean_data.csv`     --> This file will only appear if proteins from the training database have been excluded. Is the same file as _data_prot.csv_ but excluding the proteins.

Now everything is almost ready to run the DiffDock simulations. First of all an input for DiffDock is generated using `input_DD.py`, the code needs the files `data_A.csv` and `data_B.csv` and a directory with all the predicted structures. The output file will be:

6. `input_DD.csv` 

|complex_name | chainA | chainB | SMILES |
|-------------|--------|--------|--------|
|86_84_449241.0  |/structures/86.pdb |/home/ramon/juan/structures/working_structures/84.pdb |Brc1ccc(\C=C\CNCCNS(=O)(=O)c2cccc3cnccc23)cc1 |
|169_168_5362440.0|/structures/169.pdb |/home/ramon/juan/structures/working_structures/168.pdb |CC(C)(C)NC(=O)[C@@H]1CN(Cc2cccnc2)CCN1C[C@@H](O)C[C@@H](Cc1ccccc1)C(=O)N[C@@H]1[C@H](O)Cc2ccccc12 |
|... |... |... |... |


Once this file is done Diffdock is ready to run.

```bash
sbatch run_DD.sh
```
All the necessary _pdb_ files will be generated and when Diffdock ends, the results will be organized by folders and the following file will be created and stored in `clean_results´.

7. `combined.csv` --> A file containing the ID, confidence and chain to which every sample has been attached.

||ID   |Confidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |Chain(A=0)(B=1)     |
|------|-----|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
|0     |206_209_392622|-1.49                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |1                   |
|1     |206_209_392622|-1.59                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |1                   |
|2     |206_209_392622|-1.70                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |0                   |
|...|...|...|...|

This file must be included in the `/DD` directory that will appear in the directory where you are executing the `run.sh` file. If not then the program will ask you to add the file inside the corresponding directory. It is allowed to have more than one file in the `/DD` directory and all of them will be evaluated.

The program will now call `rank_formula.py` from the `/codes` directory to evaluate all the samples and establish whether the result of the docking simulation is protein A or B. In addition, a plot showing the reliability of every guess with $log(k_i^A/k_i^B)$ is provided. 

Finally, `plots.py` from the `/codes` directory will generate the rest of the plots that are placed inside `output/figures`. 
