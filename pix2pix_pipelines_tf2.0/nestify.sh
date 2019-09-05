#!/bin/bash
set -e

# ---------------------------------------------------------------------------------------------------------------
#
# TL;DR
#
# nestify.sh is a little helper shell script provided with this project and that aims to automate the
# conversion of the code from a multiple files implementations into a nested single file implementation.
# This is done by including a few tag comments in that code at the appropriate locations.
#
# Now you have the flexibity to write your pipeline code in multiple files, while having the possibility
# to define Kubeflow components using func_to_container_op, which require that all the necessary code
# (including the imports) are self-contained inside the python function defining the Kubeflow component.
# With the nestify script (and a couple of comment tags added in the source code), this can be done
# without having to duplicate/modify your code.
#
# This part is a little tips & tricks used in this project implementation, but you may want to reuse/adjust
# this approach in your own projects. Note that, this is not a Kubeflow official recommendation.
#
# (You can skip reading the details if you will)
#
# ---------------------------------------------------------------------------------------------------------------
#
# Usually this is a good idea to define the code of a componnent, like the training Pix2Pix task, in
# several python files. For example this allows to manage the model definition, and other helper functions
# separately, and makes possible to share their source code in different components (without duplication) when
# buidling docker images for Kubeflow.
#
# Now, with Kubeflow Pipelines, by using the SDK's kfp.components.func_to_container_op method , it is possible
# to convert a Python function to a pipeline component and returns a factory function. You can then call the
# factory function to construct an instance of a pipeline task (ContainerOp) that runs the original function
# in a container.
#
# This is very usefull to use this method when prototyping the code in Jupyter Notebooks, rather having to wait
# for building dedicated Docker images at each iterations. However all the necessary code (including the imports)
# must be self-contained inside that python function.
#
# Nestify is a little helper shell script provided with this project and that aims to automate the conversion of
# the code from a multiple files implementations into a nested single file implementation. This is done by
# including a few tag comment in that code at the appropriate locations.
#
# In order to include the import functions you want to reuse/nest inside another one, you have to:"
#   - in the python functions defined in files outside the main python file, which defines the Kubeflow component,
#     encapsulate that code between comment tags '#KFP-BEGIN' and '#KFP-END'.
#   - in the main python file defining the Kubeflow component, and that imports these functions, add a comment
#     tag '#KFP-NEST-IMPORT' on the same line as these imports.
#   - in the main python file, add a comment tag '#KFP-NEST-HERE' at the position these functions must be
#     embeded nested.
#
# ---------------------------------------------------------------------------------------------------------------


if [ -z "$1" ] || [ "$1" = "--help" ] || [ "$1" = "-h"  ]; then
    echo "nestify.sh is a little helper shell script provided with this project and that aims to automate the"
    echo "conversion of the code from a multiple files implementations into a nested single file implementation."
    echo "This is done by including a few tag comments in that code at the appropriate locations."
    echo "(See details in the script)"
    echo
    echo "Usage : 'nestify my_kfp_component_source_code.py' will output a 'nested_my_kfp_component_source_code.py'"
    echo "(logs are in 'nested_my_kfp_component_source_code.py'"
    exit
elif [ ! -f "$1" ]; then
    echo "$1 : File Not Found"
    exit
fi


clear

# -----------------------------------------------------------------------------
# Step 1 : Find in the source file, all the python imports tagged with
#          comment "#KFP-NEST-IMPORT"
# -----------------------------------------------------------------------------
printf "\n------------------------------- STEP 1 ------------------------------- \n" > nested_$1.log
awk '
BEGIN {
    FS=" ";
}

/#KFP-NEST-IMPORT/ { file_list[$2]}

END {
    for (i in file_list) {
        print i ".py";
    }
}

' $1 > nestify-files.tmp

printf "\n[INFO] Nestify will process the following python import files from %s: \n" >> nested_$1.log
cat nestify-files.tmp >> nested_$1.log


# -----------------------------------------------------------------------------
# Step 2 :  For each python found import files to process, extract
#           the code contained between the #KFP-BEGIN/ and #KFP-END flags
# -----------------------------------------------------------------------------
printf "\n\n------------------------------- STEP 2 ------------------------------- \n" >> nested_$1.log
echo "" > nestify-code.tmp
while read  file
do
    printf "\n[INFO] ********************* Processing $file *********************\n " >> nested_$1.log
    awk '
    BEGIN {
         p=0  # Boolean to decide to print or not
         };

    /#KFP-BEGIN/ { p = 1 ; next };
    /#KFP-END/  { p = 0 ; next };

    p { sub(/^/, "  ")};
    p { print }

    ' ${file} > nestify-partial-code.tmp
    printf "[INFO] Nestify will embbed the following code in %s : \n" $1 >> nested_$1.log
    cat nestify-partial-code.tmp >> nestify-code.tmp
    cat nestify-partial-code.tmp >> nested_$1.log

done < nestify-files.tmp

# -----------------------------------------------------------------------------
# Step 3 :  Remove imports at module level, Replace python imports tagged with
#           comment "#KFP-NEST-IMPORT" by nesting their code after the
#           "#KFP-NEST-HERE" tag position. and, Remove the "main" python code.
#           All other lines are kept.
# -----------------------------------------------------------------------------
printf "\n\n------------------------------- STEP 3 ------------------------------- \n" >> nested_$1.log
awk '

BEGIN { p=1  # Boolean to decide to print or not
};

/^from/ { next };
/^import/ { next };
/#KFP-NEST-IMPORT/ { next };
/__main__/ { p = 0 ; next };
p { print }

/#KFP-NEST-HERE/{while(getline<"nestify-code.tmp"){print}}

' $1 > nested_$1

printf "\n\n[INFO] The tagged python dependencies of $1 have been nested within $1  code inside $nested_$1\n" >> nested_$1.log
cat  nested_$1 >> nested_$1.log

#  Remove temporary files
rm nestify-*.tmp

# Return results
printf "\n\n------------------- End of Nestify processing ------------------- \n" >> nested_$1.log

printf "\nProcessing $1:"
printf "\n Logs are in ./nested_$1.log \n Output result is in ./nested_$1"
printf "\n Usage : 'import nested_$1' instead of 'import $1'\n"
printf "\n ~ End of Nestify processing ~\n\n"
