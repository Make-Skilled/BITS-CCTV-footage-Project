// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract VideoFeed {

  uint[] _streamids;
  uint[] _owners;
  string[] _dates;
  string[] _times;
  string[] _videohashes;
  string[] _locations;
  string location="Kurnool";

  uint[] _requestby;
  uint[] _requestto;
  uint[] _reqstatus;
  uint[] _reqstreamids;
  uint[] _reqids;

  uint streamid;
  uint reqid;

  constructor() {
    streamid=0;
    reqid=0;
  }

  function addVideoHash(uint owner,string memory date,string memory time,string memory videohash) public {
    streamid+=1;
    _streamids.push(streamid);
    _owners.push(owner);
    _dates.push(date);
    _times.push(time);
    _videohashes.push(videohash);
  }

  function viewHashes() public view returns(uint[] memory,uint[] memory,string[] memory,string[] memory,string[] memory) {
    return(_streamids,_owners,_dates,_times,_videohashes);
  }

  function sendrequest(uint requestby,uint requestto,uint reqstreamid) public {
    reqid+=1;
    _requestby.push(requestby);
    _requestto.push(requestto);
    _reqstreamids.push(reqstreamid);
    _reqstatus.push(0);
    _reqids.push(reqid);
  }

  function viewrequest() public view returns(uint[] memory,uint[] memory,uint[] memory,uint[] memory,uint[] memory){
    return(_requestby,_requestto,_reqstreamids,_reqstatus,_reqids);
  }

  function updaterequest(uint reid,uint restatus) public {
    uint i;
    for(i=0;i<_reqids.length;i++){
      if(_reqids[i]==reid){
        _reqstatus[i]=restatus;
      }
    }
  }
}
