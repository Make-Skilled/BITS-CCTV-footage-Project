const VideoFeed = artifacts.require('VideoFeed');

module.exports=function(deployer){
    deployer.deploy(VideoFeed);
}