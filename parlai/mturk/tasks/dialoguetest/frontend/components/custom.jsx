/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

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
import { MessageList } from "./messaging.jsx";
import { jsonToForm, QueryForm } from "./forms";
import { apartmentJson } from "./mocks.js";
import * as constants from "./constants";
import "./jitter_workaround";

class WizardResponse extends React.Component {
  constructor(props) {
    super(props);
    this.state = { textval: "", sending: false };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Only change in the active status of this component should cause a
    // focus event. Not having this would make the focus occur on every
    // state update (including things like volume changes)
    if (this.props.active && !prevProps.active) {
      $("input#id_text_input").focus();
    }
    this.props.onInputResize();
  }

  tryMessageSend(shouldSuggest) {
    if (this.state.textval != "" && this.props.active && !this.state.sending) {
      this.setState({ sending: true });

      if (shouldSuggest && !this.state.textval.startsWith("?")) {
        const selectionConstants = constants.PROTOCOL_CONSTANTS.front_to_back;
        this.props.onMessageSend(
          `${selectionConstants.request_suggestions_prefix}${this.state
            .textval}`,
          {},
          () => this.setState({ textval: "", sending: false })
        );
      } else {
        this.props.onMessageSend(this.state.textval, {}, () =>
          this.setState({ textval: "", sending: false })
        );
      }
    }
  }

  handleKeyPress(e, shouldSuggest) {
    if (e.key === "Enter") {
      this.tryMessageSend(shouldSuggest);
      e.stopPropagation();
      e.nativeEvent.stopImmediatePropagation();
    }
  }

  updateValue(value) {
    this.setState({ textval: "" + value });
  }

  render() {
    let pane_style = {
      paddingLeft: "25px",
      paddingTop: "20px",
      paddingBottom: "20px",
      paddingRight: "25px",
      float: "left",
      width: "100%"
    };
    let input_style = {
      height: "50px",
      width: "100%",
      display: "block",
      float: "left"
    };
    let submit_style = {
      height: "100%",
      fontSize: "16px",
      float: "left",
      marginLeft: "10px"
    };
    const shouldSuggest =
      this.props.messages.find(msg => msg.id === "KnowledgeBase") != null;

    let text_input = (
      <FormControl
        type="text"
        id="id_text_input"
        style={{
          width: "80%",
          height: "100%",
          float: "left",
          fontSize: "16px"
        }}
        value={this.state.textval}
        placeholder="Please enter here..."
        onKeyPress={e => this.handleKeyPress(e, shouldSuggest)}
        onChange={e => this.updateValue(e.target.value)}
        disabled={!this.props.active || this.state.sending}
      />
    );

    let submit_button = (
      <Button
        className="btn btn-primary"
        style={submit_style}
        id="id_send_msg_button"
        disabled={
          this.state.textval == "" || !this.props.active || this.state.sending
        }
        onClick={() => this.tryMessageSend(shouldSuggest)}
      >
        {shouldSuggest ? "Get Suggestions" : "Send"}
      </Button>
    );

    return (
      <div
        id="response-type-text-input"
        className="response-type-module"
        style={pane_style}
      >
        <div style={input_style}>
          {text_input}
          {submit_button}
        </div>
      </div>
    );
  }
}

function ReviewForm(props) {
  const unsure_hint = (
    <React.Fragment>
      <br />
      If you are unsure, then don't place a check mark.
      <br />
    </React.Fragment>
  );

  const hasReviewed =
    props.messages.find(
      msg => msg.id === props.agent_id && msg.text.startsWith("<done>")
    ) != null;

  return (
    <form
      onSubmit={event => {
        event.preventDefault();
        let form = event.target;
        const parameters = {};
        for (const element of form.elements) {
          const key = element.name;
          if (element.type === "checkbox") {
            parameters[key] = element.checked;
          }
        }

        props.onMessageSend(`<done> ${parameters}`, {}, () =>
          console.log("sent done with", parameters)
        );
      }}
    >
      <div>Thank you for the conversation.</div>
      <br />
      {props.agent_id === "Wizard"
        ? <div>
            Did the user...<br />

            <div style={{ marginLeft: 20 }}>
              <Checkbox name="ok_user_found">... find an apartment?</Checkbox>
              <Checkbox name="ok_user_demands">
                ... require at least 4 specific criteria?
              </Checkbox>
              <Checkbox name="ok_user_change">
                ... change his/her mind about what he/she wants at any point?
              </Checkbox>
            </div>

            {unsure_hint}
          </div>
        : <div>
            Did the assistant... <br />

            <div style={{ marginLeft: 20 }}>
              <Checkbox name="ok_wizard_found">
                ... find an apartment for you?
              </Checkbox>
              <Checkbox name="ok_wizard_bye">
                ... say goodbye at the end of the dialogue?
                {" "}
              </Checkbox>
              <Checkbox name="ok_wizard_polite">
                ... stay polite and patient throughout the conversation?
              </Checkbox>
            </div>
            {unsure_hint}
          </div>}

      <Button className="btn btn-primary" disabled={hasReviewed} type="submit">
        Confirm
      </Button>
    </form>
  );
}

function CompleteButton(props) {
  if (props.world_state === "onboarding") {
    return (
      <div id="ask_accept">
        If you are ready, please click "Accept HIT" to start this
        task.<br />
      </div>
    );
  }

  const realMessageCount = props.messages.filter(
    msg =>
      msg.text !== "" &&
      msg.command == null &&
      !msg.text.startsWith("<") &&
      msg.id !== "MTurk System"
  ).length;

  return (
    <Button
      className="btn btn-primary"
      disabled={realMessageCount < constants.FINISHABLE_MESSAGE_COUNT}
      onClick={() => {
        props.onMessageSend("<complete>", {}, () =>
          console.log("sent complete")
        );
      }}
    >
      I have completed my task
    </Button>
  );
}

function OnboardingView(props) {
  return props.agent_id === "User"
    ? <div id="task-description" style={{ fontSize: "16px" }}>
        <h1>Live Chat</h1>
        <hr style={{ borderTop: "1px solid #555" }} />
        <div>
          You recently started a <b>new job in Sydney</b> and need to find an
          apartment to live in.
          For now, you stay in a hotel, but that is expensive, so you'll
          {" "}<b>want to find something soon</b>.
          A friend of yours recommended the virtual assistant that you are
          about
          to talk to now.
          Maybe it can help you find something you like?
        </div>
        <br />

        <div>
          Your task is complete, when
          <ul>
            <li>
              You found an apartment that satisfies at least
              {" "}<b>4 specific criteria</b> of your choosing (e.g. number of
              rooms, balcony/elevator availability, etc.) - you might have to
              make some compromises to find something
            </li>
            <li>
              You have
              {" "}<b>changed your mind about what you want at least once</b>
              {" "}during the conversation
            </li>
            <li>
              You said <b>goodbye</b> (or similar) at the end of your dialogue
            </li>
          </ul>
          At the end of this dialogue, you will have to judge if the assistant
          fulfilled his/her task.<br />

          <CompleteButton {...props} />
        </div>
      </div>
    : <div id="task-description" style={{ fontSize: "16px" }}>
        <h1>Live Chat</h1>
        <hr style={{ borderTop: "1px solid #555" }} />
        <div>
          You play the role of a <b>virtual assistant</b> that helps people
          find an apartment in Sydney.
          The user that you talk to may sometimes change his/her mind and may
          not be sure what he/she wants.
          Your task is to be as helpful to the user as possible in any case,
          but
          {" "}
          <b>
            you cannot do anything but searching and discussing apartments
          </b>.
          So if the user wants you to make coffee, you should explain that you
          cannot do this.
          If you feel like you should provide the user with an example
          apartment, <b>just make up a description</b>.

          Users may even be rude or uncooperative, but you are beyond this and
          {" "}<b>always keep a patient, level tone</b>.
          <br />
        </div>
        <div>
          Your task is complete, when
          <ul>
            <li>The user has found a suitable apartment</li>
            <li>The user has said 'goodbye' (or similar)</li>
          </ul>

          At the end of this dialogue, you will have to judge if the user
          fulfilled his/her task.<br />
        </div>
        <div id="ask_accept">
          If you are ready, please click "Accept HIT" to start this task.<br />
        </div>
      </div>;
}

class TaskDescription extends React.Component {
  render() {
    if (this.props.isInReview) {
      return <ReviewForm {...this.props} />;
    }

    return <OnboardingView {...this.props} />;
  }
}

class LeftPane extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      current_pane: "instruction",
      last_update: 0,
      selectedTabKey: 2
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (
      nextProps.task_data !== undefined &&
      nextProps.task_data.last_update !== undefined &&
      nextProps.task_data.last_update > prevState.last_update
    ) {
      return {
        current_pane: "context",
        last_update: nextProps.task_data.last_update
      };
    } else return null;
  }

  handleSelectTab = key => {
    this.setState({
      selectedTabKey: key
    });
  };

  render() {
    let v_id = this.props.v_id;
    let frame_height = this.props.frame_height;
    let frame_style = {
      height: frame_height + "px",
      backgroundColor: "#fafbfc",
      padding: "30px",
      overflow: "auto"
    };

    let pane_size = this.props.is_cover_page ? "col-xs-12" : "col-xs-4";
    let has_context = this.props.task_data.has_context;
    const isInReview =
      this.props.messages.find(msg => msg.command === "review") != null;

    if (
      this.props.world_state === "onboarding" ||
      this.props.agent_id === "User" ||
      isInReview
    ) {
      return (
        <div id="left-pane" className={pane_size} style={frame_style}>
          <TaskDescription {...this.props} isInReview={isInReview} />
          {this.props.children}
        </div>
      );
    }

    const setupMessage = this.props.messages.find(
      msg => msg.command === "setup" && msg.form_description != null
    );
    if (setupMessage == null) {
      return "Waiting for initialization...";
    }

    const dbNames = setupMessage.form_description.map(desc => desc.db);

    return (
      <div id="left-pane" className={pane_size} style={frame_style}>
        <Tab.Container id="left-tabs-example" defaultActiveKey={0}>
          <Row className="clearfix">
            <Col
              sm={3}
              style={{
                marginTop: 50,
                display: dbNames.length <= 1 ? "none" : undefined
              }}
            >
              <Nav bsStyle="pills" stacked>
                {dbNames.map((tabName, idx) =>
                  <NavItem eventKey={idx}>{_.capitalize(tabName)}</NavItem>
                )}
              </Nav>
            </Col>
            <Col sm={9}>
              <Tab.Content animation={false} mountOnEnter={true}>
                {dbNames.map((dbName, dbIndex) => {
                  return (
                    <Tab.Pane
                      eventKey={dbIndex}
                      animation={false}
                      mountOnEnter={true}
                    >
                      <Tabs
                        eventKey={this.state.selectedTabKey}
                        onSelect={this.handleSelectTab}
                        animation={false}
                      >
                        <Tab eventKey={1} title="Your Instruction Schema">

                          <img
                            style={{ width: "100%" }}
                            src={
                              setupMessage.form_description[dbIndex].schema_url
                            }
                          />
                        </Tab>
                        <Tab eventKey={2} title="Knowledge Base">
                          <h4>User's requirements for {dbName}:</h4>
                          <QueryForm
                            {...this.props}
                            category={dbName}
                            formDescription={
                              setupMessage.form_description[dbIndex]
                            }
                          />
                        </Tab>
                      </Tabs>

                      <hr />
                      <CompleteButton {...this.props} />
                    </Tab.Pane>
                  );
                })}
              </Tab.Content>
            </Col>
          </Row>
        </Tab.Container>
        {this.props.children}
      </div>
    );
  }
}

export default {
  XTextResponse: {
    // default: leave blank to use original default when no ids match
    Wizard: WizardResponse
  },
  XLeftPane: {
    Wizard: LeftPane,
    User: LeftPane,
    Onboarding: LeftPane
  },
  XMessageList: {
    Wizard: MessageList,
    User: MessageList
  }
};
