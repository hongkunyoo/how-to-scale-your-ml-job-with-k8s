import os
import datetime
import jinja2


# Load pipeline-template.yaml
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "pipeline-template.yaml"
template = templateEnv.get_template(TEMPLATE_FILE)


# Insert model experiments
steps = []

steps.append({
    "name": "train0101",
    "epoch": 1,
    "activate": "relu",
    "drouput": 0.2,
    "data-path": "/wf_storage"
})

steps.append({
    "name": "train0102",
    "epoch": 2,
    "activate": "selu",
    "drouput": 0.3,
    "data-path": "/wf_storage"
})

# Render template
idx = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
rendered = template.render(wfIdx=idx, slack_url='abc', steps=steps)


# Apply workflow
cmd = """cat << EOF | kubectl apply -f -
%s
EOF
""" % rendered

os.system(cmd)
