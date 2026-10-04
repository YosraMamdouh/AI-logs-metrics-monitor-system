pipeline {
    agent any
    triggers {
        // فحص GitHub تلقائياً كل دقيقة لبدء البناء بمجرد عمل push
        pollSCM('* * * * *')
    }
    environment {
        DOCKER_IMAGE = 'yosramamdouh234/aiops-backend'
        DOCKER_CREDS_ID = 'jenkins-token'
        K8S_NAMESPACE = 'dev'
    }
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YosraMamdouh/AI-logs-metrics-monitor-system.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                dir('backend') {
                    sh '''
                        docker build \
                            -t aiops-backend:${BUILD_NUMBER} \
                            .
                    '''
                }
            }
        }
        stage('Run Unit Tests') {
            steps {
                dir('backend') {
                    sh '''
                        docker run --rm \
                            aiops-backend:${BUILD_NUMBER} \
                            python -m pytest tests/ -v -p no:cacheprovider
                    '''
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.DOCKER_CREDS_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker tag aiops-backend:${BUILD_NUMBER} ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker tag aiops-backend:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest
                        docker logout
                    '''
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" \
                        K8s_YAML/05-backend-deployment.yaml
                    kubectl apply -f K8s_YAML/
                '''
            }
        }
        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl rollout status \
                        deployment/aiops-backend \
                        -n ${K8S_NAMESPACE} \
                        --timeout=180s
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
