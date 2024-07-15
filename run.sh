#!/bin/bash
#SBATCH --mail-type=NONE # mail configuration: NONE, BEGIN, END, FAIL, REQUEUE, ALL
#SBATCH --output=/itet-stor/jiaxie/net_scratch/DeepPurposePlusPlus/jobs/%j.out # where to store the output (%j is the JOBID), subdirectory "jobs" must exist
#SBATCH --error=/itet-stor/jiaxie/net_scratch/DeepPurposePlusPlus/jobs/%j.err # where to store error messages
#SBATCH --mem=5G
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:geforce_rtx_3090:1
#SBATCH --exclude=tikgpu10
#SBATCH --nodelist=tikgpu07
#CommentSBATCH --account=tik-internal
#CommentSBATCH --constraint='titan_rtx|tesla_v100|titan_xp|a100_80gb'



ETH_USERNAME=jiaxie
PROJECT_NAME=DeepPurposePlusPlus
DIRECTORY=/itet-stor/${ETH_USERNAME}/net_scratch/${PROJECT_NAME}/train
CONDA_ENVIRONMENT=grit
# Set a directory for temporary files unique to the job with automatic removal at job termination
TMPDIR=$(mktemp -d)
if [[ ! -d ${TMPDIR} ]]; then
echo 'Failed to create temp directory' >&2
exit 1
fi
trap "exit 1" HUP INT TERM
trap 'rm -rf "${TMPDIR}"' EXIT
export TMPDIR

# Change the current directory to the location where you want to store temporary files, exit if changing didn't succeed.
# Adapt this to your personal preference
cd "${TMPDIR}" || exit 1
# Send some noteworthy information to the output log

echo "Running on node: $(hostname)"
echo "In directory: $(pwd)"
echo "Starting on: $(date)"
echo "SLURM_JOB_ID: ${SLURM_JOB_ID}"


[[ -f /itet-stor/${ETH_USERNAME}/net_scratch/conda/bin/conda ]] && eval "$(/itet-stor/${ETH_USERNAME}/net_scratch/conda/bin/conda shell.bash hook)"
conda activate ${CONDA_ENVIRONMENT}
echo "Conda activated"
cd ${DIRECTORY}

# Execute your code
#python fluroscence.py --target_encoding DGL_GCN --seed 7 --wandb_proj DeepPurposePP --lr 0.00001 --num_layers 2 --epochs 40  --batch_size 128
#python fluroscence.py --target_encoding DGL_GAT --seed 0 --wandb_proj DeepPurposePP --lr 0.00001 --num_layers 2 --epochs 40
#python fluroscence.py --target_encoding Transformer --seed 100 --wandb_proj DeepPurposePP --num_layers 2 --epochs 100
#python fluroscence.py --target_encoding CNN_RNN --seed 100 --wandb_proj DeepPurposePP --num_layers 2 --epochs 100

python beta.py --target_encoding CNN --seed 42 --wandb_proj DeepPurposePP --num_layers 2 --epochs 300 --lr 0.0001 --batch_size 64

echo "Finished at: $(date)"

# End the script with exit code 0
exit 0


