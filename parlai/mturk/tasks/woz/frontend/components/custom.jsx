/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from 'react';
import ReactDOM from 'react-dom';
import _ from 'lodash';
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
} from 'react-bootstrap';

import $ from 'jquery';
import { MessageList } from './messaging.jsx';
import { jsonToForm, QueryForm } from './forms';
import { apartmentJson } from './mocks.js';
import * as constants from './constants';
import './jitter_workaround';

const selectionConstants = constants.PROTOCOL_CONSTANTS.front_to_back;

class WizardResponse extends React.Component {
  constructor(props) {
    super(props);
    this.state = { textval: '', sending: false };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Only change in the active status of this component should cause a
    // focus event. Not having this would make the focus occur on every
    // state update (including things like volume changes)
    if (this.props.active && !prevProps.active) {
      $('input#id_text_input').focus();
    }
    this.props.onInputResize();
  }

  tryMessageSend(shouldSuggest) {
    if (this.state.textval != '' && this.props.active && !this.state.sending) {
      this.setState({ sending: true });

      if (shouldSuggest && !this.state.textval.startsWith('?')) {
        this.props.onMessageSend(
          `${selectionConstants.request_suggestions_prefix}${this.state.textval}`,
          {},
          () => this.setState({ textval: '', sending: false })
        );
      } else {
        this.props.onMessageSend(this.state.textval, {}, () =>
          this.setState({ textval: '', sending: false })
        );
      }
    }
  }

  handleKeyPress(e, shouldSuggest) {
    if (e.key === 'Enter') {
      this.tryMessageSend(shouldSuggest);
      e.stopPropagation();
      e.nativeEvent.stopImmediatePropagation();
    }
  }

  updateValue(value) {
    this.setState({ textval: '' + value });
  }

  shouldAskForSuggestion() {
    //     let shouldAskForSuggestion = false;
    //     for (const message of this.props.messages) {
    //       if (message.id === "KnowledgeBase") {
    //         shouldAskForSuggestion = true;
    //       }
    //       if (message.text.startsWith(selectionConstants.pick_suggestion_prefix)) {
    //         shouldAskForSuggestion = false;
    //       }
    //     }

    //     let shouldAskForSuggestion = (this.props.agent_id === "Wizard");
    //     if (this.props.messages.length > 2) {
    //         let msg = this.props.messages[this.props.messages.length - 1]
    //         if (msg.text.startsWith("?")) {
    //             shouldAskForSuggestion = false;
    //         }
    //         if (msg.text.startsWith("<")) {
    //             shouldAskForSuggestion = false;
    //         }
    //     }
    //     return shouldAskForSuggestion;

    //     return (this.props.agent_id === "Wizard");
    return (this.props.agent_id === "Wizard");
  }

  render() {
    let pane_style = {
      paddingLeft: '25px',
      paddingTop: '20px',
      paddingBottom: '20px',
      paddingRight: '25px',
      float: 'left',
      width: '100%',
    };
    let input_style = {
      height: '50px',
      width: '100%',
      display: 'block',
      float: 'left',
    };
    let submit_style = {
      height: '100%',
      fontSize: '16px',
      float: 'left',
      marginLeft: '10px',
    };
    const shouldSuggest = this.shouldAskForSuggestion();

    let text_input = (
      <FormControl
        type="text"
        id="id_text_input"
        style={{
          width: '80%',
          height: '100%',
          float: 'left',
          fontSize: '16px',
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
          this.state.textval == '' || !this.props.active || this.state.sending
        }
        onClick={() => this.tryMessageSend(shouldSuggest)}
      >
        {shouldSuggest ? 'Get Suggestions' : 'Send'}
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
      msg => msg.id === props.agent_id && msg.text.startsWith('<done>')
    ) != null;

  const setupMessage = props.messages.find(
    msg => msg.command === 'setup' && msg.form_description != null
  );
  if (setupMessage == null) {
    return 'Waiting for initialization...';
  }
  const completionQuestions = setupMessage.completion_questions;
  const other_agent = props.agent_id === 'User' ? 'assistant ' : 'user ';

  return (
    <form
      onSubmit={event => {
        event.preventDefault();
        let form = event.target;
        const parameters = {};
        for (const element of form.elements) {
          const key = element.name;
          if (element.type === 'checkbox') {
            parameters[key] = element.checked;
          }
        }

        const parameter_string = JSON.stringify(parameters);

        props.onMessageSend(`<done> ${parameter_string}`, {}, () =>
          console.log('sent done with', parameters)
        );
      }}
    >
      <div>Thank you for the conversation.</div>
      <br />
      <div>
        Did the {other_agent}...
        <br />
        <div style={{ marginLeft: 20 }}>
          {completionQuestions.map((q, i) => {
            return <Checkbox name={'ch_' + i}> {q} </Checkbox>;
          })}
        </div>
        {unsure_hint}
      </div>

      <Button className="btn btn-primary" disabled={hasReviewed} type="submit">
        Confirm
      </Button>
    </form>
  );
}

function CompleteButton(props) {
  if (props.world_state === 'onboarding') {
    return (
      <div id="ask_accept">
        If you are ready, please click "Accept HIT" to start this task.
        <br />
      </div>
    );
  }

  const realMessageCount = props.messages.filter(
    msg =>
      msg.text !== '' &&
      msg.command == null &&
      !msg.text.startsWith('<') &&
      msg.id !== 'MTurk System'
  ).length;

  const other_agent = props.agent_id === 'User' ? 'assistant ' : 'user ';

  return (
    <Button
      className="btn btn-primary"
      disabled={props.chat_state !== 'text_input'}
      onClick={() => {
        props.onMessageSend('<complete>', {}, () =>
          console.log('sent complete')
        );
      }}
    >
      The {other_agent} has said goodbye
    </Button>
  );
}

function OnboardingView(props) {
  const setupMessage = props.messages.find(
    msg => msg.command === 'setup' && msg.form_description != null
  );
  if (setupMessage == null) {
    return 'Waiting for initialization...';
  }
  const taskDescription = setupMessage.task_description;
  if (taskDescription == null) {
    taskDescription = 'taskDescription';
  }
  const completionRequirements = setupMessage.completion_requirements;
  const other_agent = props.agent_id === 'User' ? 'assistant ' : 'user ';

  return (
    <div id="task-description" style={{ fontSize: '16px' }}>
      <h1>Live Chat</h1>
      <hr style={{ borderTop: '1px solid #555' }} />
      <div>{taskDescription}</div>
      <br />
      <div>
        Your task is complete, when
        <ul>
          {completionRequirements.map(req => {
            return <li> {req} </li>;
          })}
        </ul>
        At the end of this dialogue, you will have to judge if the {other_agent}
        fulfilled his/her task.
        <br />
      </div>
    </div>
  );
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
      current_pane: 'instruction',
      last_update: 0,
      selectedTabKey: 2,
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (
      nextProps.task_data !== undefined &&
      nextProps.task_data.last_update !== undefined &&
      nextProps.task_data.last_update > prevState.last_update
    ) {
      return {
        current_pane: 'context',
        last_update: nextProps.task_data.last_update,
      };
    } else return null;
  }

  handleSelectTab = key => {
    this.setState({
      selectedTabKey: key,
    });
  };

  render() {
    let v_id = this.props.v_id;
    let frame_height = this.props.frame_height;
    let frame_style = {
      height: frame_height + 'px',
      backgroundColor: '#fafbfc',
      padding: '30px',
      overflow: 'auto',
    };

    let pane_size = this.props.is_cover_page ? 'col-xs-12' : 'col-xs-4';
    let has_context = this.props.task_data.has_context;
    const isInReview =
      this.props.messages.find(msg => msg.command === 'review') != null;

    if (this.props.world_state === 'onboarding') {
      return (
        <div id="left-pane" className={pane_size} style={frame_style}>
          <TaskDescription {...this.props} isInReview={isInReview} />
          {this.props.children}
          <br />
          If you are ready, please follow the instructions of the 'MTurk System' bot in the dialogue.
          <br />
        </div>
      );
    } else if (isInReview) {
      return (
        <div id="left-pane" className={pane_size} style={frame_style}>
          <TaskDescription {...this.props} isInReview={isInReview} />
          {this.props.children}
        </div>
      );
    } else if (this.props.agent_id === 'User') {
      return (
        <div id="left-pane" className={pane_size} style={frame_style}>
          <TaskDescription {...this.props} isInReview={isInReview} />
          {this.props.children}
          <hr />
          <CompleteButton {...this.props} />
        </div>
      );
    }

    const setupMessage = this.props.messages.find(
      msg => msg.command === 'setup' && msg.form_description != null
    );
    if (setupMessage == null) {
      return 'Waiting for initialization...';
    }

    //const dbNames = setupMessage.form_description.map(desc => desc.db);
    const apiNames = Object.keys(setupMessage.form_description);
    //     const taskDescription = setupMessage.task_description
    //     if (taskDescription == null) {
    //         taskDescription = "taskDescription"
    //     }

    return (
      <div id="left-pane" className={pane_size} style={frame_style}>
        <Tab.Container id="left-tabs-example" defaultActiveKey={0}>
          <Row className="clearfix">
            <Col
              sm={3}
              style={{
                marginTop: 50,
                display: apiNames.length <= 1 ? 'none' : undefined,
              }}
            >
              <Nav bsStyle="pills" stacked>
                {apiNames.map((tabName, idx) => (
                  <NavItem eventKey={idx}>
                    {_.capitalize(tabName.replace(/_/g, '\n'))}
                  </NavItem>
                ))}
              </Nav>
            </Col>
            <Col sm={9}>
              <Tab.Content animation={false} mountOnEnter={true}>
                {apiNames.map((apiName, apiIndex) => {
                  const imgUrl =
                    setupMessage.form_description[apiName].schema_url;
                  console.log(apiName);
                  return (
                    <Tab.Pane
                      eventKey={apiIndex}
                      animation={false}
                      mountOnEnter={true}
                    >
                      <Tabs
                        eventKey={this.state.selectedTabKey}
                        onSelect={this.handleSelectTab}
                        animation={false}
                      >
                        <Tab eventKey={1} title="Instructions">
                          <a href={imgUrl} target="_blank">
                            <img style={{ width: '100%' }} src={imgUrl} />
                          </a>
                        </Tab>
                        <Tab eventKey={2} title="Knowledge Base">
                          <h4>User's requirements for {apiName}:</h4>
                          <QueryForm
                            {...this.props}
                            category={apiName}
                            formDescription={
                              setupMessage.form_description[apiName]
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
    Wizard: WizardResponse,
  },
  XLeftPane: {
    Wizard: LeftPane,
    User: LeftPane,
    Onboarding: LeftPane,
    waiting: LeftPane,
  },
  XMessageList: {
    Wizard: MessageList,
    User: MessageList,
  },
};
