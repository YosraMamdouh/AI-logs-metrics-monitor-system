pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'yosramamdouh234/aiops-backend'
        DOCKER_CREDS_ID = 'jenkins-token'
        K8S_NAMESPACE = 'aiops'
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
                        for i in 1 2 3 4 5; do
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER} && break || (echo "Push timed out, retrying in 3s..." && sleep 3)
                        done
                        for i in 1 2 3 4 5; do
                            docker push ${DOCKER_IMAGE}:latest && break || (echo "Push timed out, retrying in 3s..." && sleep 3)
                        done
                        docker logout
                    '''
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl create namespace ${K8S_NAMESPACE} \
                        --dry-run=client \
                        -o yaml | kubectl apply -f -
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" \
                        K8s_YAML/05-backend-deployment.yaml
                    kubectl apply -f K8s_YAML/ \
                        -n ${K8S_NAMESPACE}
                '''
            }
        }
        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl rollout status \
                        deployment/backend-deployment \
                        -n ${K8S_NAMESPACE} \
                        --timeout=60s
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
