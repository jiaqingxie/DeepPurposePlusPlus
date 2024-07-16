import os
import sys
import argparse
import torch
import wandb

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from DeepPurpose_PP.dataset import *
import DeepPurpose_PP.utils as utils
import DeepPurpose_PP.ProteinPred as models



def parse_args():
    parser = argparse.ArgumentParser(description="Protein Prediction with DeepPurpose++")
    parser.add_argument('--target_encoding', type=str, default='CNN', help='Encoding method for target proteins')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--wandb_proj', type=str, default='your_project_name', help='wandb project name')
    parser.add_argument('--batch_size', type=int, default=32, help='16/32/64/128')
    parser.add_argument('--lr', type=float, default=0.0001, help='0.001/0.0001/0.00001')
    parser.add_argument('--num_layers', type=int, default=1, help='1/2/4/8')
    parser.add_argument('--epochs', type=int, default=20, help='20/50/100')
    parser.add_argument('--embed_dim',type=int, default=1024, help='32/128/512/1024')

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    target_encoding = args.target_encoding
    wandb_project = args.wandb_proj
    batch_size = args.batch_size
    lr = args.lr
    num_layers = args.num_layers
    epochs = args.epochs
    embed_dim = args.embed_dim

    job_name = f"Beta + {target_encoding}"
    wandb.init(project=wandb_project, name=job_name)
    wandb.config.update(args)

    # path = os.getcwd()
    path = "/itet-stor/jiaxie/net_scratch/DeepPurposePlusPlus"
    #  Test on Beta_lactamase
    train_fluo = Beta_lactamase(path + '/DeepPurpose_PP/data', 'train')
    valid_fluo = Beta_lactamase(path + '/DeepPurpose_PP/data', 'valid')
    test_fluo = Beta_lactamase(path + '/DeepPurpose_PP/data', 'test')

    if target_encoding == 'DGL_GCN' or 'DGL_GAT':
        train_protein_processed, train_target, train_protein_idx = collate_fn(train_fluo, graph = True)
        valid_protein_processed, valid_target, valid_protein_idx = collate_fn(valid_fluo, graph = True)
        test_protein_processed, test_target, test_protein_idx = collate_fn(test_fluo, graph = True)

    else:
        train_protein_processed, train_target, train_protein_idx = collate_fn(train_fluo, unsqueeze = False)
        valid_protein_processed, valid_target, valid_protein_idx = collate_fn(valid_fluo, unsqueeze = False)
        test_protein_processed, test_target, test_protein_idx = collate_fn(test_fluo, unsqueeze = False)



    train, _, _ = utils.data_process(X_target = train_protein_processed, y = train_target, target_encoding = target_encoding, 
                                        # drug_encoding= drug_encoding,
                                split_method='random',frac=[0.9998,1e-4,1e-4],
                                random_seed = 1)
    
    _, val, _ = utils.data_process(X_target = valid_protein_processed, y = valid_target, target_encoding = target_encoding,
                                        # drug_encoding= drug_encoding,
                                split_method='random',frac=[1e-4,0.9998,1e-4],
                                random_seed = 1)
    
    _, _, test = utils.data_process(X_target = test_protein_processed, y = test_target, target_encoding = target_encoding, 
                                        # drug_encoding= drug_encoding,
                                split_method='random',frac=[1e-4,1e-4,0.9998],
                                random_seed = 1)


    config = generate_config(target_encoding = target_encoding, 
                         cls_hidden_dims = [embed_dim] * num_layers,
                         train_epoch = epochs,
                         LR = lr,
                         batch_size = batch_size,
                        )
    config['gnn_num_layers'] = num_layers
    # config['gnn_hid_dim_drug'] = embed_dim
    config['hidden_dim_protein'] = embed_dim
    # config['cnn_target_filters'] = [embed_dim] * num_layers

    torch.manual_seed(args.seed)
    model = models.model_initialize(**config)
    model.train(train, val, test)


    