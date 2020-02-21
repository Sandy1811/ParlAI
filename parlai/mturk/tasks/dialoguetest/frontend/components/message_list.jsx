import React from "react";
import ReactDOM from "react-dom";
import _ from "lodash";
import {
  Glyphicon,
  Row,
  Col,
  FormControl,
  Button,
  ButtonGroup,
  InputGroup,
  FormGroup,
  MenuItem,
  DropdownButton,
  Badge,
  Checkbox,
  Radio,
  Popover,
  Overlay,
  Nav,
  NavItem,
  ControlLabel,
  Form,
  Tabs,
  Tab,
  HelpBlock
} from "react-bootstrap";

import $ from "jquery";

class ChatMessage extends React.Component {
  render() {
    let float_loc = "left";
    let alert_class = "alert-warning";
    if (this.props.is_self) {
      float_loc = "right";
      alert_class = "alert-info";
    }
    let duration = null;
    if (this.props.duration !== undefined) {
      let duration_seconds = Math.floor(this.props.duration / 1000) % 60;
      let duration_minutes = Math.floor(this.props.duration / 60000);
      let min_text = duration_minutes > 0 ? duration_minutes + " min" : "";
      let sec_text = duration_seconds > 0 ? duration_seconds + " sec" : "";
      duration = (
        <small>
          <br />
          <i>Duration: </i>
          {min_text + " " + sec_text}
        </small>
      );
    }

    const isKB = this.props.agent_id === "KnowledgeBase";
    const onlyVisibleMsg = isKB ? " (Only visible to you)" : null;
    const needle = "Example: ";
    const needlePosition = this.props.message.indexOf(needle);
    let message = this.props.message;
    if (needlePosition >= 0) {
      try {
        const exampleJson = JSON.parse(
          this.props.message
            .slice(needlePosition + needle.length, -1)
            .replace(/'/g, '"')
        );

        message = [];
        for (const key of Object.values(exampleJson)) {
          message.push(`${key}: ${exampleJson[key]}`);
        }
        message = message.join("\n");

        console.log("exampleJson", exampleJson);
      } catch (exc) {
        console.log("failed to parse example json");
      }
    }

    return (
      <div className={"row"} style={{ marginLeft: "0", marginRight: "0" }}>
        <div
          className={"alert " + alert_class}
          role="alert"
          style={{ float: float_loc, display: "table" }}
        >
          <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
            <b>{this.props.agent_id}{onlyVisibleMsg}</b>: {message}
          </span>
          {duration}
        </div>
      </div>
    );
  }
}

export class MessageList extends React.Component {
  makeMessages() {
    let agent_id = this.props.agent_id;
    let messages = this.props.messages;
    // Handles rendering messages from both the user and anyone else
    // on the thread - agent_ids for the sender of a message exist in
    // the m.id field.
    let XChatMessage = ChatMessage;
    let onClickMessage = this.props.onClickMessage;
    if (typeof onClickMessage !== "function") {
      onClickMessage = idx => {};
    }
    return messages.map((m, idx) => {
      const dontRender = m.command != null || m.text.startsWith("?");

      return dontRender
        ? null
        : <div key={m.message_id} onClick={() => onClickMessage(idx)}>
            <XChatMessage
              is_self={m.id == agent_id}
              agent_id={m.id}
              message={m.text}
              task_data={m.task_data}
              message_id={m.message_id}
              duration={this.props.is_review ? m.duration : undefined}
            />
          </div>;
    });
  }

  render() {
    return (
      <div id="message_thread" style={{ width: "100%" }}>
        {this.makeMessages()}
      </div>
    );
  }
}