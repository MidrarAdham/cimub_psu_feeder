#!/bin/bash
cd ./glm/
gridlabd -D WANT_VI_DUMP=1 Master_run.glm >Master.log
mv M*.csv ./glm/
