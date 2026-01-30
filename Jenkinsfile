pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        echo 'Building...'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing...'
        snykSecurity(
          projectName: 'DevSecOps-Pipeline',  
          snykInstallation: 'snyk-cli',
          snykTokenId: 'SNYK_TOKEN',
          // place other parameters here
          additionalArguments: 'iac test phase-5-containerization/src/Dockerfile',
          failOnIssues: false
        )
      }
    }
    stage('Deploy') {
      steps {
        echo 'Deploying...'
      }
    }
  }
}
