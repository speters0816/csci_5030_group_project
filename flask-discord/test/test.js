var assert = require('assert');
const { describe } = require('mocha');
describe('Array', function () {
	describe('#indexOf()', function () {
		it('should return -1 when the value is not present', function () {
			assert.equal([1,2,3].indexOf(4),-1);
		});
	});
});

describe('Time', function() {
	it("should convert UTC date object to local date time"), function () {
		const currentTime = new Date(Date.now());
		const msgTime = new Date("May 04 2022 03:40:57 -0600 UTC");
		console.log(msgTime);
		assert.notEqual(msgTime,currentTime);
	}
})

