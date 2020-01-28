import org.jenkinsci.plugins.pipeline.github.trigger.IssueCommentCause

@Library('pipeline-lib') _
@Library('cve-monitor') __

def MAIN_BRANCH                    = 'master'
def DOCKER_REPOSITORY_NAME         = 'dd-agent'
def DOCKER_REGISTRY_URL            = 'https://662491802882.dkr.ecr.us-east-1.amazonaws.com'
def DOCKER_REGISTRY_CREDENTIALS_ID = 'ecr:us-east-1:ecr-docker-push'

properties([
    pipelineTriggers([issueCommentTrigger('!build')])
])
def isForcePublish = !!currentBuild.rawBuild.getCause(IssueCommentCause)

withResultReporting(slackChannel: '#tm-inf') {
  inDockerAgent(containers: [imageScanner.container()]) {
    def image, imageTag
    stage('Build') {
      checkout(scm)
      def shortCommit = sh(returnStdout: true, script: 'git log -n 1 --pretty=format:"%h"').trim()
      def ddVersion = sh(returnStdout: true, script: 'grep FROM Dockerfile|cut -d ":" -f2').trim()
      imageTag = "${ddVersion}-${shortCommit}"
      ansiColor('xterm') {
        image = docker.build(DOCKER_REPOSITORY_NAME)
      }
    }
    stage('Scan image') {
      imageScanner.scan(image)
    }
    if (BRANCH_NAME == MAIN_BRANCH || isForcePublish) {
      stage('Publish docker image') {
        echo("Publishing docker image ${image.imageName()} with tag ${imageTag}")
        docker.withRegistry(DOCKER_REGISTRY_URL, DOCKER_REGISTRY_CREDENTIALS_ID) {
          image.push(imageTag)
        }
        if (isForcePublish) {
          pullRequest.comment("Built and published `${imageTag}`")
        }
      }
    } else {
      echo("${BRANCH_NAME} is not the master branch. Not publishing the docker image.")
    }
  }
}
