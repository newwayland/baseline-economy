#!/bin/sh
	cat > k8s/kustomization.yaml <<-EOF
resources:
- deployment.yaml
- service.yaml
images:
- name: baseline
  newName: ${1}
  newTag: ${2}
EOF

