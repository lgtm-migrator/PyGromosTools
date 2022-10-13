import os
from pygromos.euler_submissions.FileManager import Simulation_System as sys


def build_jobarray(script_out_path:str, output_dir:str, run_script:str, array_length:int, array_name:str, previous_ID:int=None, analysis_script=None, duration:str="24:00:00", analysis_duration:str = "4:00:00" , analysis_processors:int =1,start_pos:int = 1,  job_throttle:int=100, cpu_per_job:int=4, noFailInChain:bool=True, memory:int=None, noFail:bool=True):

    previous_job=""
    if previous_ID!=None:
        if(noFail == True):
            previous_job = f' -d "afterok:{previous_ID}" '
        else:
            previous_job = f' -d "afterany:{previous_ID}" '

    if(noFailInChain):
        chaining_prefix="afterok"
    else:
        chaining_prefix="afterany"

    if(memory != None):
        r_opt = f' --mem-per-cpu={memory} '
    else:
        r_opt = ""

    script_text =(
        "#!/usr/bin/env bash\n"
        "JOBNAME=\""+array_name+"\"\n"
        "SSTART="+str(start_pos)+"\n"
        "SEND="+str(array_length)+"\n"
        "JOBS=$(($((SEND - SSTART)) + 1 ))\n"
        "JOBLIM="+str(job_throttle)+"\n"
        "CPUPERJOB="+str(cpu_per_job)+"\n"

        "\n"
        "BASEDIR="+output_dir+"\n"
        "RUNSCRIPT="+run_script+"\n"
        "    \n"
        "# do\n"
        "mkdir -p ${BASEDIR}\n"
        "cd $BASEDIR\n"
        "echo \"Array: ${JOBNAME}[$SSTART-$SEND]\"\n"
        "echo \"reserve $CPUPERJOB CPUS per sopt_job\"\n"
        "jobID=$(sbatch  --array=${SSTART}-${SEND} " +r_opt+ "-n $CPUPERJOB --time "+duration+" -e ${BASEDIR}/${JOBNAME}.err -o ${BASEDIR}/${JOBNAME}.out "+previous_job+" -J \"${JOBNAME}[$SSTART-$SEND]%${JOBLIM}\" < $RUNSCRIPT  | awk '{print $NF}')\n"
        "echo \"$jobID\"\n"
        "cd .. \n"
    )
    if(analysis_script != None):
        script_text += (
            "\necho \"start ANA\"\n"
            "ANASCRIPT=\""+analysis_script+"\"\n"
            f'jobID=$(sbatch  -d "{chaining_prefix}:' + "${jobID}\"" + f' -n {analysis_processors} --time {analysis_duration}' + " -e ${BASEDIR}/../${JOBNAME}_ana.err -o ${BASEDIR}/../${JOBNAME}_ana.out -J \"${JOBNAME}_ana\" < ${ANASCRIPT} | awk \'{print $NF}\')\n"
            "echo \"$jobID\"\n"
        )

    script = open(script_out_path, "w")
    script.write(script_text)
    script.close()
    return script_out_path

def build_worker_script_multImds(out_script_path:str, in_system:sys.System, in_imd_prefix:str,
                                 job_name: str,
                                 out_dir: str,
                                 gromosXX_bin:str=None, cores:int=1)->str:
    """build_worker_script_multImds

        This function writes out a job script, that is a worker_scripts for a scheduled a jobarray for gromos simulations.
            So it acts as a thread for a single task. In this jobarray always the .imd Files  (e.g.: path/to/imd_prefix_[num].imd) are different.

    Parameters
    ----------
    out_script_path :   str
        output path, where the script sould be located
    in_system : fM.System
        System obj. containing all the managed files.
    in_imd_prefix : str
        prefix of the imd files, that differ (e.g.: path/to/imd_prefix_[num].imd)
    job_name :  str
        name of the scheduled job.
    out_dir :   str
        output direcotry for the simulations
    gromosXX_bin :  str
        path to gromos binary folder
    cores : int
        number of cores for this job

    Returns
    -------
    str
        out_script_path
    """

    in_imd = in_imd_prefix
    in_cnf=in_system.coordinates
    in_top = in_system.top.top_path
    in_ptp = in_system.top.perturbation_path
    
    restraint_text = " "
    gromos_res = " "
    
    if in_system.top.disres_path is not None:
        restraint_text += "DISRES=" + in_system.top.disres_path +"\n"
        gromos_res += "        @distrest    ${DISRES}\\\n"
    if in_system.top.posres_path is not None:
        restraint_text += "POSRES="+in_system.top.posres_path+"\n"
        restraint_text += "REFPOS="+in_system.top.refpos_path+"\n"

        gromos_res += "        @posresspec    ${POSRES}\\\n"
        gromos_res += "        @refpos    ${REFPOS}\\\n"

    if(gromosXX_bin== None):
        gromosXX_bin="md_mpi"
    else:
        gromosXX_bin+="/md_mpi"

    script_text = (
    "#!/usr/bin/env bash\n"
    "#RUN this script only with arry submission!\n"
    "\n"
    "SPACE=\"/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////\"\n"
    "echo -e \"$SPACE \n START Script index.rst: ${SLURM_ARRAY_TASK_ID}\"\n"
    "# first we set some variables\n"
    "NAME=\""+os.environ['USER']+"\"\n"
    "OUTPREFIX=" + job_name +"\n"
    "CORES=" + str(cores) +"\n"
    "RUNID=$SLURM_ARRAY_TASK_ID"
    "\n"

    "#DIR\n"
    "PROGRAM=" + str(gromosXX_bin) + "\n"
    "OUTDIR=${PWD}\n"
    "\n"
    "#INPUT FILES\n"
    "TOPO=" + in_top +"\n"
    ""+restraint_text+"\n"
    "PTTOPO=" + in_ptp +"\n"
    "INIMD=" + in_imd +"_${RUNID}.imd\n"
    "INPUTCRD=" + in_cnf +"\n"
    "\n"
    
    "#PREPROCESSING\n"
    "# create temporary directory\n"
    "echo -e \"Let's go to work! \n \tJOBID: ${SLURM_ARRAY_TASK_ID} \n\tProcessors: ${PROCLIMIT}\"\n"
    "WORKDIR=" + out_dir +"\n"
    "mkdir -p ${WORKDIR}\n"
    "cd       ${WORKDIR}\n"
    "\n"
    
    "#RUN:\n"
    "echo -e \"OUTPUT PREFIX: $OUTPREFIX\"\n" 
    "echo -e \"$SPACE\n STARTING Simulation executed by $NAME \n $(date)\"\n"
    "TMPOUTPREFIXEQ=${OUTPREFIX}_1_${RUNID}\n"
    "\n"
    
    "#Short_Equilibraton\n"
    "mpirun -n ${CORES} ${PROGRAM} \\\n"
    "        @topo        ${TOPO} \\\n"
    "        @conf        ${INPUTCRD} \\\n"
    "        @input       ${INIMD} \\\n"
    "        @pttopo      ${PTTOPO} \\\n"
    ""+gromos_res+"\\\n"
    "        @fin         ${TMPOUTPREFIXEQ}.cnf \\\n"

    "        @trc         ${TMPOUTPREFIXEQ}.trc \\\n"
    "        @tre         ${TMPOUTPREFIXEQ}.tre \\\n"
    "         >  ${TMPOUTPREFIXEQ}.omd\n"
    "\n")

    script = open(out_script_path, "w")
    script.write(script_text)
    script.close()
    return  out_script_path


def build_worker_script_mult_cnfs(script_out_path: str, job_name: str, system: sys.System, in_protocol_prefix: str, out_dir: str,
                                  gromosXX_bin: str=None,
                                  cores: int = 1):
    name = job_name
    in_imd = in_protocol_prefix
    in_cnf = system.coordinates[0].replace("0001", "${RUNID}").replace("0.cnf", "${RUNID}.cnf")
    in_top = system.top
    out_dir = out_dir

    if(gromosXX_bin== None):
        md_mpi="md_mpi"
    else:
        md_mpi= gromosXX_bin+"/md_mpi"

    script_text = (
            "#!/usr/bin/env bash"
            "#RUN this script only with arry submission!\n"
            "\n"
            "SPACE=\"/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////\"\n"
            "echo -e \"$SPACE \n START Script index.rst: ${SLURM_ARRAY_TASK_ID}\"\n"
            "# first we set svome variables\n"
            "NAME=\"benjamin\"\n"
            "OUTPREFIX=" + job_name + "_${SLURM_ARRAY_TASK_ID}\n"
            "CORES=" + str(cores) + "\n"
            "RUNID=$SLURM_ARRAY_TASK_ID"
            "\n"

            "#DIR\n"
            "PROGRAM=" + md_mpi + " \n"
            "OUTDIR=${PWD}\n"
            "\n"

            "#INPUT FILES\n"
            "TOPO=" + in_top + "\n"
            "INIMD=" + in_imd + "${RUNID}.imd\n"
            "if [  ${SLURM_ARRAY_TASK_ID} -gt 999 ];\n"
            "then"
            "        RUNID=\"${SLURM_ARRAY_TASK_ID}\"\n"
            "else\n"
            "  if [ ${SLURM_ARRAY_TASK_ID} -gt 99 ];\n"
            "  then\n"
            "        RUNID=\"0${SLURM_ARRAY_TASK_ID}\"\n"
            "  else\n"
            "    if [ ${SLURM_ARRAY_TASK_ID} -gt 9 ];\n"
            "    then\n"
            "        RUNID=\"00${SLURM_ARRAY_TASK_ID}\"\n"
            "    else\n"
            "        RUNID=\"000${SLURM_ARRAY_TASK_ID}\"\n"
            "    fi\n"
            "  fi\n"
            "fi\n"
            "INPUTCRD=" + in_cnf + "\n"
             "\n"
             "#PREPROCESSING\n"
             "# create temporary directory\n"
             "echo -e \"Let's go to work! \n \tJOBID: ${RUNID} \n\tProcessors: ${PROCLIMIT}\"\n"
             "WORKDIR=" + out_dir + "\n"
             "mkdir -p ${WORKDIR}\n"
             "cd       ${WORKDIR}\n"
             "\n"
             "#RUN:\n"
             "echo -e \"OUTPUT PREFIX: $OUTPREFIX\"\n"
             "echo -e \"$SPACE\n STARTING SImulation executed by $NAME \n $(date)\"\n"
             "TMPOUTPREFIXEQ=\"" + out_dir + "/" + name + "_${RUNID}\"\n"
             "\n"
             "#Short_Equilibraton\n"
                 "mpirun -n ${CORES} ${PROGRAM} \\\n"
                 "        @topo        ${TOPO} \\\n"
                 "        @conf        ${INPUTCRD} \\\n"
                 "        @input       ${INIMD} \\\n"
                 "        @pttopo      ${PTTOPO} \\\n"
                 "        @distrest    ${DISRES} \\\n"
                 "        @fin         ${TMPOUTPREFIXEQ}.cnf \\\n"
                 "        @trc         ${TMPOUTPREFIXEQ}.out_trc \\\n"
                 "        @tre         ${TMPOUTPREFIXEQ}.out_tre \\\n"
                 "         >  ${TMPOUTPREFIXEQ}.omd\n"
                 "\n")

    script = open(script_out_path, "w")
    script.write(script_text)
    script.close()
    return script_out_path
