// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract CCTVFootage {

  string adminEmail;
  string adminPassword;

  uint[] _pids;
  string[] _pname;
  string[] _pemail;
  string[] _ppassword;
  uint[] _pstatuses;

  uint[] _gids;
  string[] _gname;
  string[] _gemail;
  string[] _gpassword;
  uint[] _gstatuses;

  mapping(string=>bool) _registeredPrivate;
  mapping(string=>bool) _registeredGovt;

  uint pid;
  uint gid;

  constructor() {
    pid=0;
    gid=0;
    adminEmail="admin@admin.com";
    adminPassword="admin123";
  }

  function viewAdmin() public view returns(string memory,string memory){
    return (adminEmail,adminPassword);
  }

  function addPrivateOfficial(string memory name,string memory email,string memory password) public{

    require(!_registeredPrivate[email]);

    pid+=1;
    _pname.push(name);
    _pemail.push(email);
    _ppassword.push(password);
    _pids.push(pid);
    _pstatuses.push(0);

    _registeredPrivate[email]=true;
  } 

  function viewPrivateOfficial() public view returns(uint[] memory,string[] memory,string[] memory,string[] memory,uint[] memory){
    return(_pids,_pname,_pemail,_ppassword,_pstatuses);
  }

  function addGovernmentOfficial(string memory name,string memory email,string memory password) public {
    require(!_registeredGovt[email]);

    gid+=1;
    _gname.push(name);
    _gemail.push(email);
    _gpassword.push(password);
    _gids.push(pid);
    _gstatuses.push(0);

    _registeredGovt[email]=true;
  }

  function viewGovernmentOfficial() public view returns(uint[] memory,string[] memory,string[] memory,string[] memory,uint[] memory){
    return(_gids,_gname,_gemail,_gpassword,_gstatuses);
  }

  function updateGovernmentOfficial(uint gid1,uint status1) public {
    uint i;
    for(i=0;i<_gids.length;i++){
      if(_gids[i]==gid1){
        _gstatuses[i]=status1;
      }
    }
  }

  function updatePrivateOfficial(uint pid1,uint status2) public {
    uint i;
    for(i=0;i<_pids.length;i++){
      if(_pids[i]==pid1){
        _pstatuses[i]=status2;
      }
    }
  }

}
