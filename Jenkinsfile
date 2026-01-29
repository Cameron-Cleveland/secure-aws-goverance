pipeline {
    agent any

    environment {
        // Update these two for your specific environment
        VM_IP = "172.188.40.16" 
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
                withCredentials([string(credentialsId: '1.26_snyk_API', variable: 'SNYK_TOKEN')]) {
                    script {
                        echo "Running Snyk Security Scans..."
                        sh "snyk auth $SNYK_TOKEN"
                        // Scans your PHP dependencies and your AWS/Azure Terraform files
                        // We use || true so the pipeline continues even if it finds issues, for testing purposes
                        sh "snyk test || true"
                        sh "snyk iac test || true"
                    }
                }
            }
        }

        stage('Build: PHP Container') {
            steps {
                script {
                    // This creates the image locally on your Azure VM
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    sh "docker build -t ${imageTag} ."
                    echo "Image Built: ${imageTag}"
                }
            }
        }

        stage('Security: Image Scan (Trivy)') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    echo "Scanning Image for Vulnerabilities..."
                    // Fails the build if CRITICAL issues are found
                    sh "trivy image --severity CRITICAL --exit-code 1 ${imageTag}"
                }
            }
        }

        stage('Infrastructure: Terraform Plan') {
            steps {
                // Using your 3 specific Azure Secret IDs
                withCredentials([
                    string(credentialsId: 'Azure Application ID', variable: 'AZ_CLIENT_ID'),
                    string(credentialsId: 'Azure-Secrets-ID', variable: 'AZ_CLIENT_SECRET'),
                    string(credentialsId: 'Directory ID', variable: 'AZ_TENANT_ID')
                ]) {
                    script {
                        // Azure Terraform Authentication
                        env.ARM_CLIENT_ID = AZ_CLIENT_ID
                        env.ARM_CLIENT_SECRET = AZ_CLIENT_SECRET
                        env.ARM_TENANT_ID = AZ_TENANT_ID
                        
                        sh '''
                            terraform init
                            terraform plan -out=tfplan
                            echo "Terraform Plan successfully generated."
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "PoC SUCCESS: Code is scanned, Image is built, and Infra Plan is validated."
        }
        failure {
            echo "PoC FAILED: Check console logs for security violations or syntax errors."
        }
    }
}
