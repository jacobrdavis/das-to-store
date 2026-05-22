#!/bin/bash
#SBATCH --job-name=kerchunk_das-onyx      	 # Job name
#SBATCH --output=%x_%j.out          	     # Standard output file
#SBATCH --error=%x_%j.err 	   	             # Standard error file
#SBATCH --mem=128G			                 # Total amount of memory
#SBATCH --nodes=1   			             # Number of nodes
#SBATCH --ntasks-per-node=1 		         # Number of tasks per node
#SBATCH --cpus-per-task=1 		             # Number of CPU cores per task
#SBATCH --time=12:00:00      	        	 # Maximum runtime (D-HH:MM:SS)
#SBATCH --mail-type=END                      # Send email at job completion
#SBATCH --mail-user=jacob.davis@whoi.edu     # Email address for notifications

module load miniconda/25.9

. $CONDA_PREFIX/etc/profile.d/conda.sh

conda activate das-to-store

python ./scripts/kerchunk_das-onyx.py
