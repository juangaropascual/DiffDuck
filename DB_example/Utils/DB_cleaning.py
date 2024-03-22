import numpy as np
from rdkit import Chem
import pandas as pd
from scipy.stats import sem
from difflib import SequenceMatcher
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import warnings
# uncomment the following line for interactive window (pip install ipympl):
# %matplotlib widget 

def read_file(file_path,columns,display_col_names=False):
    """
    Reads a tab-separated values file and returns a pandas dataframe.

    Args:
        file_path (str): The path to the file to be read.
        columns (List[str]): A list of the columns from the file that the user wants to extract.
        display_col_names (bool): Whether to display the column names. Default
        
    Returns:
        pandas.DataFrame: A pandas dataframe containing the selected data from the file.
    """
    if file_path.endswith('.tsv'):
        df = pd.read_csv(file_path, sep='\t',low_memory=False)  # Use '\t' as the delimiter
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path,low_memory=False)
    else:
        raise ValueError('File format not supported. Data base must be a tsv or csv')
    
    if display_col_names:
        for col in df.columns:
            print(col)
    df = df[columns]
    return df

def clean_df(df, n_atoms=8, seq_lim=500, AF=False,out_file='data_prot.csv', af_out='AF_input.csv'):
    """
    Cleans the dataframe by: 
            --> Removing rows that have Nan values
            --> Removing rows that have Ki values including > symbol (i.e. >100000)
            --> Removing rows that contain ligands smaller than n_atoms
            --> Removing rows that contain Ki = 0  
            --> Adding a column with the mean value of Ki for every lig-to-protein interaction
            --> Adding a column with the standard deviation of the mean Ki for every lig-to-protein interaction (if it is only one value then it is set to 0)
            --> Adding a column with the SMILES of every ligand
            --> Adding a column with the protein IDs

    Args:
        df (pandas.DataFrame): The dataframe to be cleaned.
        n_atoms (int, optional): The minimum number of atoms in a ligand for it to be included in the dataframe. Defaults to 8.
        seq_lim (int, optional): the maximum fasta length for a protein to be selected. Defaults to 500.
        AF (bool): Whether to create or not an input file for Alphafold. Default is False.

    Returns:
        pandas.DataFrame: The cleaned dataframe.
        Saves the dataframe on data_prot.csv
    """

    # delete all rows that contain Nan values
    pd.set_option('future.no_silent_downcasting', True)
    df = df.dropna() 
    df = df.reset_index(drop=True)

    # delete all rows that contain sequences longer than seq_lim
    df = df[df['BindingDB Target Chain Sequence'].str.len() <= seq_lim]
    df = df.reset_index(drop=True)

    smiles = []
    for value in range(len(df['Ki (nM)'])):
        try:
            df.loc[value, "Ki (nM)"] = float(df.loc[value, "Ki (nM)"])
        except ValueError:
            df = df.drop([value])
    df = df.reset_index(drop=True)

    save_smiles = df[['Ligand SMILES','PubChem CID']]
    df = df.groupby(['BindingDB Target Chain Sequence','PubChem CID'])["Ki (nM)"].agg([('ki_mean','mean'),('ki_sem','sem')]).reset_index()
    df = df.fillna(0)

    df = df[df.duplicated(subset=['PubChem CID'],keep=False)]
    df = df.reset_index(drop=True)

    for i,cid in enumerate(df['PubChem CID']):

        s = save_smiles[save_smiles['PubChem CID']==cid]
        s = s['Ligand SMILES'].values[0]
        mol = Chem.MolFromSmiles(s)
        num_atoms = mol.GetNumAtoms()

        # delete rows that contain small ligands
        if num_atoms <= n_atoms:
            df = df.drop([i]) 
            df = df.reset_index(drop=True)
        else:
            smiles.append(s)
    
    df['SMILES'] = smiles

    # Cal treure els que tinguin ki=0?
    df = df[df['ki_mean']!= 0]
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    df['ID'] = df.index # set protein IDs as the index of the dataframe as a provisional mesure.

    unique_seq = np.unique(df['BindingDB Target Chain Sequence']) # check the number of different proteins

    # rename all indexes if necessary
    af = pd.DataFrame({'id':[], 'sequence':[]})
    if len(unique_seq) != len(df['ID']):
        for i,seq in enumerate(unique_seq):
            df.loc[df['BindingDB Target Chain Sequence'] == seq, 'ID'] = i
            
            if AF:
                row = {'id':f"'{str(i)}'", 'sequence':seq}
                af.loc[0 if pd.isnull(af.index.max()) else af.index.max() + 1] = row

 
    df.to_csv(f'output/{out_file}')

    if AF:
        af.to_csv(f'output/{af_out}')
        print(f'* {af_out} generated from {out_file} data.')

    print('')
    print(f'* Clean data saved in {out_file}')

    return df


def seq_similarity(df):
    """
    This function compares the sequences of the different protein chains in the dataframe and prints the ones that are most similar.

    Args:
        df (pd.DataFrame): The dataframe containing the protein sequences and their affinities.

    Returns:
        None

    """
    
    un_lig = np.unique(list(df['SMILES']))
    
    for lig in range(len(un_lig)):
        sel = df[df['SMILES'] == un_lig[lig]]
        seq = list(sel['BindingDB Target Chain Sequence'])
        a=0
        for s1 in range(len(seq)):
            for s2 in range(s1+1, len(seq)):

                r = SequenceMatcher(None, seq[s1], seq[s2]).ratio()
                if r > 0.8:
                    print(r,s1,s2)
                    a=1
        if a==1:
            print(un_lig[lig])
            print('')

def sort_AB(df, threshold=0.1, out_A='data_A.csv', out_B='data_B.csv'):

    """
    This function sorts the dataframe by the affinity of the proteins with the same ligand.

    Args:
        df (pd.DataFrame): The dataframe to be sorted.
        threshold (float, optional): The threshold for sorting. Defaults to 0.1.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two dataframes, the rows of this dataframes can
        be paired by index to obtain two proteins that have different affinities with the same ligand. The data
        is sorted such as the affinity of the ligan with prot A is always higher than the one for B.
    """

    # create the new dataframes where proteins will be sorted by their affinity with the same ligand
    columns = ['Prot ID','Sequence','SMILES','Ki (nM)','ki SEM','PubChem CID']
    df_out_a = pd.DataFrame(columns=columns)
    df_out_b = pd.DataFrame(columns=columns)


    unique = np.unique(df['SMILES']) # unique ligands

    for lig in unique:

        slice = df[df['SMILES'] == lig] # obtain the slice of the dataframe that contains the ligand
        ratios = np.array(slice['ki_mean'])[:, None] / np.array(slice['ki_mean']) # ki_j/ki_k

        indices = np.indices(ratios.shape)
        id_slice = list(slice['ID'])

        prot = list(slice['BindingDB Target Chain Sequence'])
        ki = list(slice['ki_mean'])
        ki_sem = list(slice['ki_sem'])
        pub_cid = list(slice['PubChem CID'])


        mask = ratios < threshold # select only the proteins that have a ratio lower than threshold

        # since the threshold is less than 1, the most affine prot will be the one dividing
        indices_B = indices[0][mask]
        indices_A = indices[1][mask]
        ratios = ratios[mask]
        
        rows_a = []
        rows_b = []

        # Fill the new dataframes
        for i in range(len(indices_A)):

            # if len(df_out_a) == 0:
            #     df_out_a[]

            rows_a.append({'Prot ID':id_slice[indices_A[i]],
                            'Sequence':prot[indices_A[i]],
                            'SMILES':lig,
                            'Ki (nM)':ki[indices_A[i]],
                            'ki SEM': ki_sem[indices_A[i]],
                            'PubChem CID':pub_cid[indices_A[i]]})

            rows_b.append({'Prot ID':id_slice[indices_B[i]],
                            'Sequence':prot[indices_B[i]],
                            'SMILES':lig,
                            'Ki (nM)':ki[indices_B[i]],
                            'ki SEM': ki_sem[indices_B[i]],
                            'PubChem CID':pub_cid[indices_B[i]]})

        r_a = pd.DataFrame(rows_a)
        r_b = pd.DataFrame(rows_b)

        df_out_a = pd.concat([df_out_a if not df_out_a.empty else None, r_a], ignore_index=True)
        df_out_b = pd.concat([df_out_b if not df_out_b.empty else None, r_b], ignore_index=True)

    df_out_a.to_csv(f'output/{out_A}')
    df_out_b.to_csv(f'output/{out_B}')
    print(f'*** {out_A} and {out_B} successfully generated.')
    
    return df_out_a,df_out_b
    

def plot_ab(dfa,dfb, threshold=0.1, counts_graph=False, filename=None):

    """
    This function plots the dataframes dfa and dfb, where dfa contains the affinities of proteins A with the same ligand, and dfb contains the affinities of proteins
    B with the same ligand.

    Args:
        dfa (pd.DataFrame): The dataframe containing the affinities of proteins A with the same ligand.
        dfb (pd.DataFrame): The dataframe containing the affinities of proteins B with the same ligand.
        threshold (float, optional): The threshold used for sorting. Defaults to 0.1.
        counts_graph (bool, optional): If True, a histogram of the ligand counts is plotted alongside the error bars. Defaults to False.
        filename (str, optional): The name of the file containing the DD guess. Defaults to None.

    Returns:
        None

    """

    x = np.array(dfa['Ki (nM)'])
    y = np.array(dfb['Ki (nM)'])

    err_x = np.array(dfa['ki SEM'])/x
    err_y = np.array(dfb['ki SEM'])/y

    mask_x = err_x != 0
    mask_y = err_y!= 0

    mask = mask_x | mask_y
    err_x = err_x[mask]
    err_y = err_y[mask]

    x_err = x[mask]
    y_err = y[mask]

    c_list = cm.viridis(np.linspace(0, 1, 4))

    if counts_graph:
        un_lig, counts = np.unique(df['SMILES'],return_counts=True)
        col = []

        for lig in dfa['SMILES']:
            col.append(counts[list(un_lig).index(lig)])

    else:
        col = pd.read_csv(filename)
        col = list(col['0'])

    x = np.log(x)
    y = np.log(y)

    x_err = np.log(x_err)
    y_err = np.log(y_err)

    x_values = np.linspace(min(min(x),min(y)), max(max(x),max(y)), 100)

    plt.figure(figsize=(20,15))
    if counts_graph:
        plt.errorbar(x_err, y_err, yerr=err_y, xerr=err_x, ecolor='r', capsize=5,fmt='none', zorder=0)
        plt.scatter(x,y, c=col,cmap='viridis')
    else:
        plt.errorbar(x_err, y_err, yerr=err_y, xerr=err_x, ecolor='r', capsize=5,fmt='none', zorder=0)
        plt.scatter(x,y, c=col,cmap='PiYG') # 'RdYlGn'

    plt.plot(x_values, x_values, label='$log(K_i^A) = log(K_i^B)$', color=c_list[0])
    plt.plot(x_values, x_values+np.log(threshold), color=c_list[1] , label=f'$log(K_i^B/K_i^A)$ = {threshold}')
    
    plt.xlabel(fr'$log(K_i^A)$', fontsize=35)
    plt.ylabel(fr'$log(K_i^B)$', fontsize=35)
    plt.legend(fontsize=35)
    plt.xticks(fontsize=35)
    plt.yticks(fontsize=35)
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=35)
    if counts_graph:
        cbar.set_label('Ligand counts', fontsize=35)
    else:
        cbar.set_label('DiffDock guess', fontsize=35)
    plt.tight_layout()
    plt.savefig('output/figures/ka_kb.pdf')
    plt.show()


def drop_if_in_training(filename,df, AF=True, out_file='clean_data.csv',af_out='AF_input.csv'):
    """
    This function removes the proteins that are included in the training of Diffusion Distance from the dataframe.

    Args:
        filename (str): The path to the file containing the proteins that were in the training data.
        df (pd.DataFrame): The dataframe containing the protein sequences and their affinities.
        AF (bool): Whether to create or not an input file for Alphafold. Default is True.

    Returns:
        pd.DataFrame: The dataframe without the proteins included in the training.

    """
    df_drop = pd.read_csv(filename)
    df = df.drop(list(df_drop['0']))
    df = df.reset_index(drop=True)

    # If you need an AlphaFold input file:
    if AF:
        unique_seq = np.unique(df['BindingDB Target Chain Sequence'])
        af = pd.DataFrame({'id':[], 'sequence':[]})
        for i,seq in enumerate(unique_seq):
            id = df[df['BindingDB Target Chain Sequence']==seq]['ID'].values[0]
            row = {'id':f"'{str(id)}'", 'sequence':seq}
            af.loc[0 if pd.isnull(af.index.max()) else af.index.max() + 1] = row
        
        af.to_csv(f'output/{af_out}')
        print(f'** {af_out} generated from {out_file} data.')

    df.to_csv(f'output/{out_file}')

    print(f'** Removed proteins included in training of DD. Data is in {out_file}')

    return df
    

if __name__ == '__main__':
    
    # load the database
    filename = 'database/Database_example.tsv'
    columns = ['Ligand SMILES','Target Name','Ki (nM)','BindingDB Target Chain Sequence','PubChem CID']
    thresh = .1
    df = read_file(filename,columns)
    
    #select the useful rows of the database
    df = clean_df(df,n_atoms=0) # --> data_prot.csv can be used for searching in the training database (PDBBind) the matching sequences.

    # Print the similarity of the chains among each other for every ligand
    # seq_similarity(df) 

    # check if the selected target proteins are in the DD training databases
    df2 = drop_if_in_training('database/pdbbind_match_example.csv',df) # --> clean_data.csv can be used for creating the protein PDB files (i.e. AlphaFold)

    # Sort the values of the final database in a way that kiA > kiB
    dfa,dfb = sort_AB(df2,threshold=thresh) # --> data_A.csv, data_B.csv files can be paired to run the DiffDock simulation
    # plot the final database
    plot_ab(dfa,dfb, counts_graph=True,threshold=thresh)