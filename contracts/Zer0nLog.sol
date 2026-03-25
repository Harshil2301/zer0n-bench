// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Zer0nLog
 * @dev Immutable logging for vulnerability assessment reports.
 */
contract Zer0nLog {
    struct LogEntry {
        bytes32 reportHash;
        uint256 timestamp;
        address auditor;
        bool verified;
    }

    // Mapping from Report Hash -> Log Definition
    mapping(bytes32 => LogEntry) public logs;

    event LogMinted(bytes32 indexed hash, address indexed auditor);

    /**
     * @dev Anchors a vulnerability report hash to the blockchain.
     * @param _hash SHA-256 hash of the analysis report.
     */
    function logVulnerabilityHash(bytes32 _hash) public {
        require(logs[_hash].timestamp == 0, "Hash already exists");
        
        logs[_hash] = LogEntry({
            reportHash: _hash,
            timestamp: block.timestamp,
            auditor: msg.sender,
            verified: false
        });

        emit LogMinted(_hash, msg.sender);
    }

    /**
     * @dev Verifies if a hash exists and returns timestamp/auditor.
     */
    function verifyHash(bytes32 _hash) public view returns (bool, uint256, address) {
        if (logs[_hash].timestamp == 0) {
            return (false, 0, address(0));
        }
        return (true, logs[_hash].timestamp, logs[_hash].auditor);
    }
}
