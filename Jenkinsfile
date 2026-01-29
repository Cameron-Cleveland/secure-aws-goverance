pipeline {
    agent any

    environment {
        VM_IP = "65.52.198.39" 
        JFROG_REPO = "tf-terraform" 
        APP_NAME = "healthcare-php-app"
    }

    stages {
        stage('Git: Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Security: SCA & IaC Scan (Snyk)') {
            steps {
                withCredentials([string(credentialsId: 'SNYK_TOKEN_TEXT', variable: 'SNYK_TOKEN')]) {
                    script {
                        def snykTool = tool 'snyk-cli'
                        echo "Finding Snyk binary..."
                        def snykPath = sh(script: "find ${snykTool} -name snyk -type f", returnStdout: true).trim()
                        
                        sh "${snykPath} test --token=${SNYK_TOKEN} --severity-threshold=high || true"
                        sh "${snykPath} iac test --token=${SNYK_TOKEN} || true"
                    }
                }
            }
        }

        stage('Build: PHP Container') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    sh "docker build -t ${imageTag} ."
                }
            }
        }

        stage('Security: Image Scan (Trivy)') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    sh "trivy image --severity CRITICAL --exit-code 0 ${imageTag}"
                }
            }
        }

        stage('Infrastructure: Terraform Plan') {
            steps {
                withCredentials([
                    string(credentialsId: 'Application ID', variable: 'AZ_CLIENT_ID'),
                    string(credentialsId: 'Azure-Secrets-ID', variable: 'AZ_CLIENT_SECRET'),
                    string(credentialsId: 'Directory ID', variable: 'AZ_TENANT_ID')
                ]) {
                    script {
                        sh "terraform init"
                        sh "terraform plan"
                    }
                }
            }
        }

        stage('Deploy: Push to Artifactory') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    // This logs into your JFrog instance and pushes the image
                    withCredentials([usernamePassword(credentialsId: 'JFROG_CREDENTIALS', usernameVariable: 'JF_USER', passwordVariable: 'JF_PASS')]) {
                        sh "docker login ${VM_IP}:8082 -u ${JF_USER} -p ${JF_PASS}"
                        sh "docker push ${imageTag}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Very important for your 1GB VM to prevent the disk from filling up
            cleanWs()
        }
    }
}
