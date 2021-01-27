#! /bin/bash
_includeFile=$(type -p overrides.inc)
if [ ! -z ${_includeFile} ]; then
  . ${_includeFile}
else
  _red='\033[0;31m'; _yellow='\033[1;33m'; _nc='\033[0m'; echo -e \\n"${_red}overrides.inc could not be found on the path.${_nc}\n${_yellow}Please ensure the openshift-developer-tools are installed on and registered on your path.${_nc}\n${_yellow}https://github.com/BCDevOps/openshift-developer-tools${_nc}"; exit 1;
fi

# ================================================================================================================
# Special deployment parameters needed for injecting a user supplied settings into the deployment configuration
# ----------------------------------------------------------------------------------------------------------------

if createOperation; then
  # Ask the user to supply the sensitive parameters ...
  readParameter "SMTP_EMAIL_HOST - Please provide the host name of the email server:" SMTP_EMAIL_HOST "smtp.host.io"
  readParameter "STAFF_EMAILS - Please provide any staff emails" STAFF_EMAILS "addr@mail.com"
else
  # Secrets are removed from the configurations during update operations ...
  printStatusMsg "Update operation detected ...\nSkipping the prompts for WALLET_SEED secret... \n"
  writeParameter "SMTP_EMAIL_HOST" $(getSecret "${NAME}-email-host" "email-host") "false"
  writeParameter "STAFF_EMAILS" $(getSecret "${NAME}-staff-emails" "staff-emails") "false"
fi

SPECIALDEPLOYPARMS="--param-file=${_overrideParamFile}"
echo ${SPECIALDEPLOYPARMS}
