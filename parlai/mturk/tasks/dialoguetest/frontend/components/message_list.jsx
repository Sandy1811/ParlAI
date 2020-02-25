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
  HelpBlock,
  ToggleButtonGroup,
  ToggleButton
} from "react-bootstrap";

import $ from "jquery";
import * as constants from "./constants";

function getSelectionInfo(originalMessages) {
  let selectedMessage = null;
  let compareToMessage = null;

  for (const msg of originalMessages.slice().reverse()) {
    if (msg.command === "<select_message>" && selectedMessage == null) {
      selectedMessage = "todo";
    } else if (msg.id === "KnowledgeBase" && selectedMessage == null) {
      selectedMessage = "todo";
    } else if (
      msg.command === "<compare_to_message>" &&
      compareToMessage == null
    ) {
      compareToMessage = "todo";
    }

    if (selectedMessage != null && compareToMessage != null) {
      break;
    }
  }

  return {
    selectedMessage,
    compareToMessage
  };
}

function renderKnowledgeBaseMessage(message, selectionInfo) {
  const needle = "Example: ";
  const needlePosition = message.indexOf(needle);

  const { selectedMessage, compareToMessage } = selectionInfo;

  let toggleValue;
  if (message === selectedMessage) {
    toggleValue = "selected";
  } else if (message === compareToMessage) {
    toggleValue = "compare_to";
  } else {
    toggleValue = "not_selected";
  }

  if (needlePosition === -1) {
    return message;
  }

  const regex = /Found ([0-9]+)/;
  let count = null;
  const m = regex.exec(message);
  if (m != null) {
    // The result can be accessed through the `m`-variable.
    count = m[1];
    console.log("count", count);
  }
  let exampleJson;
  try {
    exampleJson = JSON.parse(message.slice(needlePosition + needle.length, -1));
  } catch (exc) {
    console.log("Failed to parse example JSON.");
  }
  if (exampleJson != null) {
    const rows = Object.keys(exampleJson).map((key, idx) => {
      let value = exampleJson[key];
      if (typeof value === "boolean") {
        value = value ? "yes" : "no";
      }

      return (
        <tr key={key}>
          <td>{key}:</td>
          <td>{value}</td>
        </tr>
      );
    });
    message = (
      <div>
        {count > 1 ? <span>This and {count - 1} matches exist:</span> : null}
        <table style={{ borderStyle: "none" }}>{rows}</table>
        <br />

        <ToggleButtonGroup type="radio" name="options" value={toggleValue}>
          <ToggleButton value={"selected"}>selected</ToggleButton>
          <ToggleButton value={"compare_to"}>compare to</ToggleButton>
          <ToggleButton value={"not_selected"}>not selected</ToggleButton>
        </ToggleButtonGroup>
      </div>
    );
  }

  return message;
}

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
    let message = isKB
      ? renderKnowledgeBaseMessage(this.props.message, this.props.selectionInfo)
      : this.props.message;

    return (
      <div
        className={"row"}
        style={{
          marginLeft: "0",
          marginRight: "0",
          backgroundColor: this.props.invisible ? "#ff2300cf" : "default"
        }}
      >
        <div
          className={"alert " + alert_class}
          role="alert"
          style={{
            float: float_loc,
            display: "table",
            backgroundColor: onlyVisibleMsg ? "#FDEFB6" : undefined,
            color: onlyVisibleMsg ? "rgb(88, 90, 94)" : undefined
          }}
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
    let onClickMessage = this.props.onClickMessage;
    if (typeof onClickMessage !== "function") {
      onClickMessage = idx => {};
    }

    const selectionInfo = getSelectionInfo(this.props.messages);

    return messages.map((m, idx) => {
      const dontRender =
        m.command != null ||
        m.text.startsWith("?") ||
        (m.text.startsWith("<") && m.text.endsWith(">"));

      return dontRender && !constants.DEBUG_FLAGS.RENDER_INVISIBLE_MESSAGES
        ? null
        : <div key={m.message_id} onClick={() => onClickMessage(idx)}>
            <ChatMessage
              is_self={m.id == agent_id}
              invisible={dontRender}
              agent_id={m.id}
              message={m.text}
              task_data={m.task_data}
              message_id={m.message_id}
              duration={this.props.is_review ? m.duration : undefined}
              selectionInfo={selectionInfo}
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
