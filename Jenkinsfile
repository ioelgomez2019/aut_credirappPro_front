pipeline {
    agent any

    stages {
        stage('Install dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3.12 -m venv .venv'
                        sh '.venv/bin/python -m pip install -r requirements.txt'
                    } else {
                        bat 'py -3.12 -m venv .venv'
                        bat '.venv\\Scripts\\python -m pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Smoke tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '.venv/bin/python -m pytest -m smoke --alluredir=reporting/allureResults --junitxml=reporting/junit.xml'
                    } else {
                        bat '.venv\\Scripts\\python -m pytest -m smoke --alluredir=reporting/allureResults --junitxml=reporting/junit.xml'
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reporting/junit.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'reporting/allureResults/**, reporting/screenshots/**'
        }
    }
}
