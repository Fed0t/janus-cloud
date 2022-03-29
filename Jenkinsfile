node('worker') {
    def image
    def deploy_env = env.JOB_NAME == "streams-janus-proxy-prod" ? "prod": "dev"
    def kubernetes = deploy_env == "prod" ?  "https://6d8996e3-40c6-4ac5-b695-05c30764f92b.k8s.ondigitalocean.com" :  "https://6d8996e3-40c6-4ac5-b695-05c30764f92b.k8s.ondigitalocean.com"

    stage('Clone repository') {
        checkout scm
    }
    stage('Build image') {
        image = docker.build('registry.digitalocean.com/streams/streams-' + deploy_env + '-janus-proxy', '-f Dockerfile ./')
    }
    stage('Push image') {
        docker.withRegistry('https://registry.digitalocean.com/streams', 'digitalocean') {
            image.push("${env.BUILD_NUMBER}")
            image.push('latest')
        }
    }
    stage ('get kubectl credentials') {
        withCredentials([usernamePassword   (credentialsId: 'digitalocean', usernameVariable: 'USERNAME', passwordVariable: 'TOKEN')]) {
            sh 'doctl auth init --access-token $TOKEN'
            sh 'doctl kubernetes cluster kubeconfig save streams-' + deploy_env + ' --access-token $TOKEN'
        }
    }
    stage('deploy') {
        sh 'kubectl config view'
        sh 'kubectl rollout restart deployment streams-janus-proxy'
        sh 'kubectl rollout restart daemonset streams-janus'
    }
}
